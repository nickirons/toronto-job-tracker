"""The Muse API fetcher - free, no authentication required."""
import httpx
from typing import List, Optional
from datetime import datetime
from backend.models.job import JobData


class MuseFetcher:
    """Fetches jobs from The Muse API (free, focuses on internships/entry-level)."""

    BASE_URL = "https://www.themuse.com/api/public/jobs"

    # Categories relevant to tech internships
    CATEGORIES = [
        "Software Engineering",
        "Data Science",
        "IT",
        "Design and UX",
        "Data Analytics",
    ]

    # Internship keywords for filtering
    INTERN_KEYWORDS = ["intern", "co-op", "coop", "internship"]

    # Exclude keywords
    EXCLUDE_KEYWORDS = ["senior", "sr.", "lead", "manager", "director", "principal", "staff"]

    async def fetch_muse_jobs(self) -> List[JobData]:
        """
        Fetch internship jobs from The Muse API.

        Returns:
            List of JobData objects filtered for internships
        """
        print(" The Muse: Fetching internship jobs...")

        all_jobs = []

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                # Fetch internship-level jobs
                # The Muse has a "level" parameter with "Internship" as an option
                params = {
                    "level": "Internship",
                    "page": 1,
                }

                # Add categories as multiple params
                for category in self.CATEGORIES:
                    params_with_cat = {**params, "category": category}

                    try:
                        response = await client.get(
                            self.BASE_URL,
                            params=params_with_cat,
                            headers={"User-Agent": "TorontoJobTracker/1.0"}
                        )

                        if response.status_code == 200:
                            data = response.json()
                            jobs = data.get("results", [])

                            for job in jobs:
                                job_data = self._parse_job(job)
                                if job_data:
                                    all_jobs.append(job_data)

                    except Exception as e:
                        print(f"   The Muse category '{category}' error: {e}")

                    # Small delay between requests
                    import asyncio
                    await asyncio.sleep(0.2)

                # Also fetch without category filter to get more results
                try:
                    response = await client.get(
                        self.BASE_URL,
                        params={"level": "Internship", "page": 1},
                        headers={"User-Agent": "TorontoJobTracker/1.0"}
                    )

                    if response.status_code == 200:
                        data = response.json()
                        jobs = data.get("results", [])

                        for job in jobs:
                            job_data = self._parse_job(job)
                            if job_data:
                                all_jobs.append(job_data)

                except Exception as e:
                    print(f"   The Muse general fetch error: {e}")

        except Exception as e:
            print(f" The Muse error: {e}")
            return []

        # Deduplicate by URL
        seen_urls = set()
        unique_jobs = []
        for job in all_jobs:
            if job.url not in seen_urls:
                seen_urls.add(job.url)
                unique_jobs.append(job)

        print(f" The Muse: Found {len(unique_jobs)} internship jobs")
        return unique_jobs

    def _parse_job(self, job: dict) -> Optional[JobData]:
        """Parse a Muse job into JobData."""
        name = job.get("name")  # Job title
        company = job.get("company", {}).get("name")
        refs = job.get("refs", {})
        url = refs.get("landing_page")

        if not all([name, company, url]):
            return None

        # Get location
        locations = job.get("locations", [])
        location = "Remote"
        for loc in locations:
            loc_name = loc.get("name", "")
            if loc_name:
                location = loc_name
                break

        # Filter for Canada/Toronto if possible, but keep all since internships are limited
        # The Muse doesn't have many Canadian jobs, so we keep all internships

        # Double-check it's an internship (title should contain intern keywords)
        title_lower = name.lower()

        # Must not contain senior/lead keywords in title
        has_exclude = any(kw in title_lower for kw in self.EXCLUDE_KEYWORDS)
        if has_exclude:
            return None

        # Get publication date
        publication_date = job.get("publication_date")
        posted_date = None
        if publication_date:
            try:
                posted_date = datetime.fromisoformat(publication_date.replace("Z", "+00:00"))
            except Exception:
                pass

        # Get description/contents
        contents = job.get("contents", "")

        return JobData(
            title=name,
            company=company,
            location=location,
            url=url,
            source="TheMuse",
            description=contents,
            posted_date=posted_date,
            is_startup=False,
        )
