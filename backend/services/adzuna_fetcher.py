"""Adzuna API fetcher - free tier with excellent Toronto coverage."""
import httpx
from typing import List, Optional
from datetime import datetime
from backend.models.job import JobData
from backend.config import get_adzuna_credentials


class AdzunaFetcher:
    """Fetches jobs from Adzuna API (free tier, great for Canadian jobs)."""

    # Canada endpoint
    BASE_URL = "https://api.adzuna.com/v1/api/jobs/ca/search"

    # Search queries for internships
    SEARCH_QUERIES = [
        "software intern",
        "developer intern",
        "data science intern",
        "co-op software",
        "internship software",
        "tech intern",
        "ai intern"
    ]

    # IT category ID for Adzuna
    CATEGORY = "it-jobs"

    # Internship keywords for filtering
    INTERN_KEYWORDS = ["intern", "co-op", "coop", "internship"]

    # Exclude keywords
    EXCLUDE_KEYWORDS = ["senior", "sr.", "lead", "manager", "director", "principal", "staff"]

    async def fetch_adzuna_jobs(self) -> List[JobData]:
        """
        Fetch internship jobs from Adzuna API.

        Returns:
            List of JobData objects filtered for internships
        """
        app_id, app_key = get_adzuna_credentials()

        if not app_id or not app_key:
            print(" Adzuna: No API credentials configured (optional)")
            return []

        print(" Adzuna: Fetching Toronto internship jobs...")

        all_jobs = []

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                for query in self.SEARCH_QUERIES:
                    try:
                        # Search in Toronto area
                        params = {
                            "app_id": app_id,
                            "app_key": app_key,
                            "what": query,
                            "where": "toronto",
                            "category": self.CATEGORY,
                            "results_per_page": 50,
                            "max_days_old": 20,
                            "sort_by": "date",
                        }

                        response = await client.get(
                            f"{self.BASE_URL}/1",
                            params=params,
                            headers={"User-Agent": "TorontoJobTracker/1.0"}
                        )

                        if response.status_code == 200:
                            data = response.json()
                            jobs = data.get("results", [])

                            for job in jobs:
                                job_data = self._parse_job(job)
                                if job_data:
                                    all_jobs.append(job_data)

                            print(f"   Adzuna '{query}': Found {len(jobs)} jobs")

                        elif response.status_code == 401:
                            print("   Adzuna: Invalid API credentials")
                            break
                        else:
                            print(f"   Adzuna '{query}' HTTP {response.status_code}")

                    except Exception as e:
                        print(f"   Adzuna '{query}' error: {e}")

                    # Small delay between requests
                    import asyncio
                    await asyncio.sleep(0.3)

        except Exception as e:
            print(f" Adzuna error: {e}")
            return []

        # Deduplicate by URL
        seen_urls = set()
        unique_jobs = []
        for job in all_jobs:
            if job.url not in seen_urls:
                seen_urls.add(job.url)
                unique_jobs.append(job)

        print(f" Adzuna: Total {len(unique_jobs)} unique internship jobs")
        return unique_jobs

    def _parse_job(self, job: dict) -> Optional[JobData]:
        """Parse an Adzuna job into JobData."""
        title = job.get("title")
        company = job.get("company", {}).get("display_name", "Unknown")
        url = job.get("redirect_url")

        if not all([title, url]):
            return None

        title_lower = title.lower()
        description = job.get("description", "").lower()

        # Must contain internship keywords in title or description
        has_intern = any(
            kw in title_lower or kw in description
            for kw in self.INTERN_KEYWORDS
        )

        if not has_intern:
            return None

        # Must not contain senior/lead keywords in title
        has_exclude = any(kw in title_lower for kw in self.EXCLUDE_KEYWORDS)
        if has_exclude:
            return None

        # Get location
        location = job.get("location", {}).get("display_name", "Toronto, ON")

        # Get salary
        salary = None
        min_salary = job.get("salary_min")
        max_salary = job.get("salary_max")
        if min_salary and max_salary:
            salary = f"CAD {int(min_salary):,}-{int(max_salary):,}/year"
        elif min_salary:
            salary = f"CAD {int(min_salary):,}/year"

        # Get posted date
        created = job.get("created")
        posted_date = None
        if created:
            try:
                posted_date = datetime.fromisoformat(created.replace("Z", "+00:00"))
            except Exception:
                pass

        return JobData(
            title=title,
            company=company,
            location=location,
            url=url,
            source="Adzuna",
            salary=salary,
            description=job.get("description", ""),
            posted_date=posted_date,
            is_startup=False,
        )
