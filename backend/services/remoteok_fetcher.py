"""RemoteOK API fetcher."""
import httpx
from typing import List, Optional
from backend.models.job import JobData


class RemoteOKFetcher:
    """Fetches jobs from RemoteOK API."""

    API_URL = "https://remoteok.com/api"

    # Internship keywords
    INTERN_KEYWORDS = ["intern", "co-op", "coop", "internship"]

    # Exclude keywords (for title)
    EXCLUDE_KEYWORDS = ["senior", "sr.", "lead", "manager", "director", "principal", "staff"]

    async def fetch_remoteok_jobs(self) -> List[JobData]:
        """
        Fetch jobs from RemoteOK API.

        Returns:
            List of JobData objects (filtered for internships)
        """
        print(" RemoteOK: Fetching jobs...")

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    self.API_URL,
                    headers={"User-Agent": "TorontoJobTracker/1.0"}
                )

                if response.status_code != 200:
                    print(f"   RemoteOK HTTP error: {response.status_code}")
                    return []

                data = response.json()

                # First element is metadata, skip it
                jobs = data[1:] if len(data) > 1 else []

                results = []
                for job in jobs:
                    job_data = self._parse_job(job)
                    if job_data:
                        results.append(job_data)

                print(f" RemoteOK: Found {len(results)} intern/junior jobs")
                return results

        except Exception as e:
            print(f" RemoteOK error: {e}")
            return []

    def _parse_job(self, job: dict) -> Optional[JobData]:
        """Parse a RemoteOK job into JobData."""
        title = job.get("position")
        company = job.get("company")
        url = job.get("url")

        if not all([title, company, url]):
            return None

        title_lower = title.lower()
        tags = " ".join(job.get("tags", [])).lower()
        description = (job.get("description") or "").lower()

        # Must contain internship keywords
        has_intern = any(
            kw in title_lower or kw in tags or kw in description
            for kw in self.INTERN_KEYWORDS
        )

        if not has_intern:
            return None

        # Must not contain senior/lead keywords in title
        has_exclude = any(kw in title_lower for kw in self.EXCLUDE_KEYWORDS)

        if has_exclude:
            return None

        return JobData(
            title=title,
            company=company,
            location=job.get("location", "Remote"),
            url=url,
            source="RemoteOK",
            description=job.get("description"),
            is_startup=True,
        )
