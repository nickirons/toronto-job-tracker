"""JSearch API client for fetching jobs from RapidAPI."""
import httpx
from typing import List, Optional
from datetime import datetime
import re
from backend.models.job import JobData
from backend.config import settings, get_rapidapi_key


class JSearchClient:
    """Client for JSearch API via RapidAPI."""

    def __init__(self):
        self.base_url = settings.jsearch_base_url
        self.host = settings.jsearch_host

    async def search_jobs(self, query: str) -> List[JobData]:
        """
        Search for jobs using JSearch API.

        Args:
            query: Search query string

        Returns:
            List of JobData objects
        """
        api_key = get_rapidapi_key()
        if not api_key:
            print("   JSearch API key not configured")
            return []

        print(f"   JSearch: Searching for '{query}'")

        url = f"{self.base_url}/search"
        params = {
            "query": query,
            "page": "1",
            "num_pages": "3",
            "date_posted": "month",
            "remote_jobs_only": "false",
        }
        headers = {
            "X-RapidAPI-Key": api_key,
            "X-RapidAPI-Host": self.host,
        }

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url, params=params, headers=headers)

                if response.status_code != 200:
                    print(f"   JSearch error: {response.status_code}")
                    print(f"   Response: {response.text[:200]}")
                    return []

                data = response.json()
                jobs = data.get("data", [])

                results = []
                for job in jobs:
                    job_data = self._parse_job(job)
                    if job_data:
                        results.append(job_data)

                print(f"   JSearch: Found {len(results)} jobs for '{query}'")
                return results

        except Exception as e:
            print(f"   JSearch error: {e}")
            return []

    def _parse_job(self, job: dict) -> Optional[JobData]:
        """Parse a JSearch job into JobData."""
        title = job.get("job_title")
        company = job.get("employer_name")
        url = job.get("job_apply_link")

        if not all([title, company, url]):
            return None

        # Format location
        city = job.get("job_city", "")
        state = job.get("job_state", "")
        location = ", ".join(filter(None, [city, state])) or "Toronto, ON"

        # Format salary
        salary = self._format_salary(job)

        # Parse date
        posted_date = self._parse_date(job.get("job_posted_at_datetime_utc"))

        # Extract duration from description
        description = job.get("job_description", "")
        duration = self._extract_duration(description)

        return JobData(
            title=title,
            company=company,
            location=location,
            url=url,
            source="JSearch",
            salary=salary,
            description=description,
            posted_date=posted_date,
            duration=duration,
            is_startup=False,
        )

    def _format_salary(self, job: dict) -> Optional[str]:
        """Format salary information."""
        min_salary = job.get("job_min_salary")
        max_salary = job.get("job_max_salary")
        currency = job.get("job_salary_currency", "CAD")
        period = job.get("job_salary_period", "YEAR")

        if not min_salary:
            return None

        period_str = period.lower() if period else "year"

        if max_salary:
            return f"{currency} {int(min_salary)}-{int(max_salary)}/{period_str}"
        return f"{currency} {int(min_salary)}/{period_str}"

    def _parse_date(self, date_str: Optional[str]) -> Optional[datetime]:
        """Parse ISO8601 date string."""
        if not date_str:
            return None
        try:
            return datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        except Exception:
            return None

    def _extract_duration(self, description: str) -> Optional[str]:
        """Extract internship duration from description."""
        if not description:
            return None

        lowered = description.lower()

        patterns = [
            (r"16[\s-]?month", "16 months"),
            (r"12[\s-]?month", "12 months"),
            (r"8[\s-]?month", "8 months"),
            (r"4[\s-]?month", "4 months"),
        ]

        for pattern, duration in patterns:
            if re.search(pattern, lowered):
                return duration

        return None

    async def search_all_queries(self) -> List[JobData]:
        """
        Search all configured queries.

        Returns:
            Combined list of JobData from all queries
        """
        # Check if API key is configured - if not, skip entirely
        api_key = get_rapidapi_key()
        if not api_key:
            print(" JSearch: Skipped (no API key configured - this is optional)")
            return []

        all_jobs = []

        for query in settings.search_queries:
            jobs = await self.search_jobs(query)
            all_jobs.extend(jobs)
            # Small delay between requests
            import asyncio
            await asyncio.sleep(0.3)

        print(f" JSearch: Total {len(all_jobs)} jobs from all queries")
        return all_jobs
