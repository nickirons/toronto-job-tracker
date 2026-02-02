"""Main job fetcher orchestrator."""
import asyncio
from typing import List, Tuple
from datetime import datetime
from sqlalchemy.orm import Session

from backend.models.job import Job, JobData
from backend.services.jsearch_client import JSearchClient
from backend.services.github_fetcher import GitHubFetcher
from backend.services.indeed_fetcher import IndeedFetcher
from backend.services.remoteok_fetcher import RemoteOKFetcher
from backend.services.arbeitnow_fetcher import ArbeitnowFetcher
from backend.services.muse_fetcher import MuseFetcher
from backend.services.adzuna_fetcher import AdzunaFetcher
from backend.services.jobspy_fetcher import JobSpyFetcher
from backend.utils.filters import filter_internships
from backend.utils.url_utils import normalize_url
from backend.utils.url_resolver import resolve_jobs_urls


class JobFetcher:
    """Main orchestrator for fetching jobs from all sources."""

    def __init__(self):
        self.jsearch = JSearchClient()
        self.github = GitHubFetcher()
        self.indeed = IndeedFetcher()
        self.remoteok = RemoteOKFetcher()
        self.arbeitnow = ArbeitnowFetcher()
        self.muse = MuseFetcher()
        self.adzuna = AdzunaFetcher()
        self.jobspy = JobSpyFetcher()
        self.last_refresh: datetime = None

    async def fetch_all_jobs(self, db: Session) -> Tuple[int, int]:
        """
        Fetch jobs from all sources, deduplicate, filter, and save to database.

        Args:
            db: Database session

        Returns:
            Tuple of (new_jobs_count, total_jobs_count)
        """
        print("=" * 60)
        print("🔄 STARTING JOB FETCH FROM ALL SOURCES")
        print("=" * 60)

        # Fetch from all sources concurrently
        # JobSpy scrapes LinkedIn, Indeed, Glassdoor for top-tier companies
        results = await asyncio.gather(
            self._fetch_jobspy(),     # Scrapes LinkedIn, Indeed, Glassdoor - best quality!
            self._fetch_adzuna(),     # Free tier with API key - good Toronto coverage
            self._fetch_github(),     # Curated lists
            self._fetch_remoteok(),   # Remote jobs
            self._fetch_jsearch(),    # Optional - only if API key configured
            return_exceptions=True
        )

        # Collect all jobs
        all_jobs: List[JobData] = []
        source_counts = {
            "JobSpy": 0,
            "Adzuna": 0,
            "GitHub": 0,
            "RemoteOK": 0,
            "JSearch": 0,
        }

        source_names = ["JobSpy", "Adzuna", "GitHub", "RemoteOK", "JSearch"]
        for i, result in enumerate(results):
            source = source_names[i]
            if isinstance(result, Exception):
                print(f"   {source} error: {result}")
            elif result:
                # JobSpy returns jobs with source like "JobSpy-Indeed", count them together
                if source == "JobSpy":
                    source_counts[source] = len(result)
                else:
                    source_counts[source] = len(result)
                all_jobs.extend(result)

        print()
        print("=" * 60)
        print("📊 FETCH SUMMARY BY SOURCE:")
        print("-" * 60)
        for source, count in source_counts.items():
            print(f"   {source}: {count} jobs")
        print("-" * 60)
        print(f"   TOTAL BEFORE DEDUP: {len(all_jobs)} jobs")

        # Deduplicate by URL
        seen_urls = set()
        unique_jobs: List[JobData] = []
        for job in all_jobs:
            normalized = normalize_url(job.url)
            if normalized not in seen_urls:
                seen_urls.add(normalized)
                unique_jobs.append(job)

        print(f"   TOTAL AFTER DEDUP: {len(unique_jobs)} jobs")

        # Filter for internships
        internship_jobs = filter_internships(unique_jobs)
        print(f"   TOTAL AFTER FILTER: {len(internship_jobs)} jobs")
        print("=" * 60)

        # Resolve application portal URLs
        print()
        print("🔗 RESOLVING APPLICATION PORTAL URLs...")
        print("-" * 60)
        internship_jobs = await resolve_jobs_urls(internship_jobs)
        print("=" * 60)

        # Save to database
        new_count = self._save_jobs(db, internship_jobs)

        self.last_refresh = datetime.utcnow()

        return new_count, len(internship_jobs)

    async def _fetch_jsearch(self) -> List[JobData]:
        """Fetch from JSearch API."""
        try:
            return await self.jsearch.search_all_queries()
        except Exception as e:
            print(f" JSearch error: {e}")
            return []

    async def _fetch_github(self) -> List[JobData]:
        """Fetch from GitHub curated lists."""
        try:
            return await self.github.fetch_curated_jobs()
        except Exception as e:
            print(f" GitHub error: {e}")
            return []

    async def _fetch_indeed(self) -> List[JobData]:
        """Fetch from Indeed RSS."""
        try:
            return await self.indeed.fetch_indeed_jobs()
        except Exception as e:
            print(f" Indeed error: {e}")
            return []

    async def _fetch_remoteok(self) -> List[JobData]:
        """Fetch from RemoteOK API."""
        try:
            return await self.remoteok.fetch_remoteok_jobs()
        except Exception as e:
            print(f" RemoteOK error: {e}")
            return []

    async def _fetch_arbeitnow(self) -> List[JobData]:
        """Fetch from Arbeitnow API."""
        try:
            return await self.arbeitnow.fetch_arbeitnow_jobs()
        except Exception as e:
            print(f" Arbeitnow error: {e}")
            return []

    async def _fetch_muse(self) -> List[JobData]:
        """Fetch from The Muse API (free, no auth needed)."""
        try:
            return await self.muse.fetch_muse_jobs()
        except Exception as e:
            print(f" The Muse error: {e}")
            return []

    async def _fetch_adzuna(self) -> List[JobData]:
        """Fetch from Adzuna API (free tier)."""
        try:
            return await self.adzuna.fetch_adzuna_jobs()
        except Exception as e:
            print(f" Adzuna error: {e}")
            return []

    async def _fetch_jobspy(self) -> List[JobData]:
        """Fetch from JobSpy (scrapes LinkedIn, Indeed, Glassdoor)."""
        try:
            return await self.jobspy.fetch_jobspy_jobs()
        except Exception as e:
            print(f" JobSpy error: {e}")
            return []

    def _save_jobs(self, db: Session, jobs: List[JobData]) -> int:
        """
        Save jobs to database, skipping duplicates.

        Returns:
            Number of new jobs added
        """
        # Get existing URLs
        existing_jobs = db.query(Job.url).all()
        existing_urls = set(normalize_url(j.url) for j in existing_jobs)

        new_count = 0
        for job_data in jobs:
            normalized_url = normalize_url(job_data.url)

            # Skip if already exists
            if normalized_url in existing_urls:
                continue

            # Create new job
            job = Job(
                title=job_data.title,
                company=job_data.company,
                location=job_data.location,
                url=job_data.url,
                apply_url=job_data.apply_url,  # Direct application portal URL
                source=job_data.source,
                salary=job_data.salary,
                description=job_data.description,
                posted_date=job_data.posted_date,
                duration=job_data.duration,
                is_startup=job_data.is_startup,
            )
            db.add(job)
            existing_urls.add(normalized_url)
            new_count += 1

        if new_count > 0:
            db.commit()
            print(f"✅ Saved {new_count} new jobs")

        return new_count


# Global instance
job_fetcher = JobFetcher()
