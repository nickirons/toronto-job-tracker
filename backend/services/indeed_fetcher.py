"""Indeed RSS feed fetcher."""
import httpx
import re
from typing import List
from backend.models.job import JobData
from backend.config import settings


class IndeedFetcher:
    """Fetches jobs from Indeed Canada RSS feeds."""

    BASE_URL = "https://ca.indeed.com/rss"

    async def fetch_indeed_jobs(self) -> List[JobData]:
        """
        Fetch jobs from Indeed RSS feeds.

        Returns:
            List of JobData objects
        """
        all_jobs = []

        print(" Indeed RSS: Starting to fetch...")

        for query in settings.indeed_queries:
            try:
                jobs = await self._fetch_query(query)
                print(f"   Indeed '{query}': Found {len(jobs)} jobs")
                all_jobs.extend(jobs)

                # Small delay between requests
                import asyncio
                await asyncio.sleep(0.2)

            except Exception as e:
                print(f"   Indeed '{query}' error: {e}")

        print(f" Indeed RSS: Total {len(all_jobs)} jobs")
        return all_jobs

    async def _fetch_query(self, query: str) -> List[JobData]:
        """Fetch a single Indeed RSS query."""
        url = f"{self.BASE_URL}?q={query}&l=Toronto%2C+ON&sort=date"

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                url,
                headers={"User-Agent": "TorontoJobTracker/1.0"}
            )

            if response.status_code != 200:
                print(f"   Indeed HTTP error: {response.status_code}")
                return []

            return self._parse_rss(response.text)

    def _parse_rss(self, xml_content: str) -> List[JobData]:
        """Parse Indeed RSS XML."""
        jobs = []

        # Simple XML parsing - split by <item>
        items = xml_content.split("<item>")

        for item in items[1:]:  # Skip first (header)
            # Extract title
            title_match = re.search(r"<title>(?:<!\[CDATA\[)?(.+?)(?:\]\]>)?</title>", item, re.DOTALL)
            if not title_match:
                continue
            full_title = title_match.group(1).strip()

            # Extract link
            link_match = re.search(r"<link>(.+?)</link>", item)
            if not link_match:
                continue
            link = link_match.group(1).strip()

            # Parse title - usually "Job Title - Company"
            parts = full_title.split(" - ")
            job_title = parts[0].strip() if parts else full_title
            company = parts[-1].strip() if len(parts) > 1 else "Unknown"

            # Filter for internships
            title_lower = full_title.lower()
            if not any(kw in title_lower for kw in ["intern", "co-op", "coop"]):
                continue

            jobs.append(JobData(
                title=job_title,
                company=company,
                location="Toronto, ON",
                url=link,
                source="Indeed",
                is_startup=False,
            ))

        return jobs
