"""Arbeitnow API fetcher."""
import httpx
from typing import List, Optional
from backend.models.job import JobData


class ArbeitnowFetcher:
    """Fetches jobs from Arbeitnow API."""

    API_URL = "https://arbeitnow.com/api/job-board-api"

    # Internship keywords
    INTERN_KEYWORDS = ["intern", "co-op", "coop", "internship"]

    # Exclude keywords (for title)
    EXCLUDE_KEYWORDS = ["senior", "sr.", "lead", "manager", "director", "principal", "staff"]

    # Canadian location keywords
    CANADIAN_LOCATIONS = ["canada", "toronto", "remote"]

    async def fetch_arbeitnow_jobs(self) -> List[JobData]:
        """
        Fetch jobs from Arbeitnow API.

        Returns:
            List of JobData objects (filtered for Canadian internships)
        """
        print(" Arbeitnow: Fetching jobs...")

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    self.API_URL,
                    headers={"User-Agent": "TorontoJobTracker/1.0"}
                )

                if response.status_code != 200:
                    print(f"   Arbeitnow HTTP error: {response.status_code}")
                    return []

                data = response.json()
                jobs = data.get("data", [])

                results = []
                for job in jobs:
                    job_data = self._parse_job(job)
                    if job_data:
                        results.append(job_data)

                print(f" Arbeitnow: Found {len(results)} Canadian intern jobs")
                return results

        except Exception as e:
            print(f" Arbeitnow error: {e}")
            return []

    def _parse_job(self, job: dict) -> Optional[JobData]:
        """Parse an Arbeitnow job into JobData."""
        title = job.get("title")
        company = job.get("company_name")
        url = job.get("url")

        if not all([title, company, url]):
            return None

        title_lower = title.lower()
        location = job.get("location", "")
        location_lower = location.lower()
        description = (job.get("description") or "").lower()
        is_remote = job.get("remote", False)

        # Must contain internship keywords
        has_intern = any(
            kw in title_lower or kw in description
            for kw in self.INTERN_KEYWORDS
        )

        if not has_intern:
            return None

        # Must be in Canada/Toronto/Remote
        has_location = (
            any(loc in location_lower for loc in self.CANADIAN_LOCATIONS) or
            is_remote
        )

        if not has_location:
            return None

        # Must not contain senior/lead keywords in title
        has_exclude = any(kw in title_lower for kw in self.EXCLUDE_KEYWORDS)

        if has_exclude:
            return None

        return JobData(
            title=title,
            company=company,
            location=location if location else "Remote",
            url=url,
            source="Arbeitnow",
            description=job.get("description"),
            is_startup=True,
        )
