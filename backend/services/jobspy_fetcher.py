"""JobSpy fetcher - scrapes LinkedIn, Indeed, Glassdoor, ZipRecruiter directly."""
import asyncio
from typing import List, Optional
from datetime import datetime
from backend.models.job import JobData


class JobSpyFetcher:
    """Fetches jobs by scraping major job boards using JobSpy library."""

    # Search queries for CS/tech internships
    # Core roles + "hidden title" variations that often contain good roles
    SEARCH_QUERIES = [
        # Core software roles
        "software engineer intern",
        "software developer intern",
        "software co-op",
        "backend engineer intern",
        "frontend developer intern",
        # Data/ML roles
        "data science intern",
        "data engineer intern",
        "machine learning intern",
        # Infrastructure
        "cloud engineer intern",
        "devops intern",
        "platform engineer intern",
        # Hidden title variations (often have good roles)
        "technology intern",
        "computer science intern",
        "solutions engineer intern",
        "automation intern",
        # QA/Testing
        "qa intern",
        "qa engineer intern",
        "test automation intern",
        "sdet intern",
        # AI/Digital
        "ai intern",
        "artificial intelligence intern",
        "digital transformation intern",
        # Bank/Fintech titles
        "technology analyst intern",
        "it developer intern",
        # Co-op variations
        "data engineer co-op",
        "qa co-op",
        "cloud engineer co-op",
        "ml engineer co-op",
        # Security/Embedded
        "security engineer intern",
        "embedded engineer intern",
        "firmware intern",
    ]

    # Sites to scrape (LinkedIn has best quality but rate limits)
    SITES = ["indeed", "linkedin", "glassdoor"]

    # Internship keywords for filtering
    INTERN_KEYWORDS = ["intern", "co-op", "coop", "internship"]

    # Exclude keywords
    EXCLUDE_KEYWORDS = ["senior", "sr.", "lead", "manager", "director", "principal", "staff"]

    async def fetch_jobspy_jobs(self) -> List[JobData]:
        """
        Fetch internship jobs by scraping LinkedIn, Indeed, Glassdoor.

        Returns:
            List of JobData objects
        """
        print(" JobSpy: Scraping LinkedIn, Indeed, Glassdoor...")

        all_jobs = []

        # Run synchronous jobspy in thread pool to not block async
        loop = asyncio.get_event_loop()

        for query in self.SEARCH_QUERIES:
            try:
                jobs = await loop.run_in_executor(
                    None,
                    self._scrape_query,
                    query
                )
                all_jobs.extend(jobs)
                print(f"   JobSpy '{query}': Found {len(jobs)} jobs")

                # Delay between queries to avoid rate limiting
                await asyncio.sleep(2)

            except Exception as e:
                print(f"   JobSpy '{query}' error: {e}")

        # Deduplicate by URL
        seen_urls = set()
        unique_jobs = []
        for job in all_jobs:
            if job.url not in seen_urls:
                seen_urls.add(job.url)
                unique_jobs.append(job)

        print(f" JobSpy: Total {len(unique_jobs)} unique internship jobs")
        return unique_jobs

    def _scrape_query(self, query: str) -> List[JobData]:
        """Synchronous scraping for a single query."""
        try:
            from jobspy import scrape_jobs

            # Scrape jobs from multiple sites
            jobs_df = scrape_jobs(
                site_name=self.SITES,
                search_term=query,
                location="Toronto, ON, Canada",
                results_wanted=80,  # Per site (increased from 25 to catch more jobs)
                hours_old=480,  # Last 7 days
                country_indeed="Canada",
            )

            if jobs_df is None or jobs_df.empty:
                return []

            results = []
            for _, row in jobs_df.iterrows():
                job_data = self._parse_job(row)
                if job_data:
                    results.append(job_data)

            return results

        except Exception as e:
            print(f"      JobSpy scrape error: {e}")
            return []

    def _parse_job(self, row) -> Optional[JobData]:
        """Parse a JobSpy result row into JobData."""
        title = str(row.get("title", "")) if row.get("title") else ""
        company = str(row.get("company", "")) if row.get("company") else ""
        job_url = str(row.get("job_url", "")) if row.get("job_url") else ""

        if not all([title, company, job_url]):
            return None

        title_lower = title.lower()
        description = str(row.get("description", "")).lower() if row.get("description") else ""

        # Must contain internship keywords
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
        location = str(row.get("location", "Toronto, ON")) if row.get("location") else "Toronto, ON"

        # Get salary
        salary = None
        min_amount = row.get("min_amount")
        max_amount = row.get("max_amount")
        interval = row.get("interval", "yearly")

        if min_amount and max_amount:
            salary = f"${int(min_amount):,}-${int(max_amount):,}/{interval}"
        elif min_amount:
            salary = f"${int(min_amount):,}/{interval}"

        # Get posted date
        posted_date = None
        date_posted = row.get("date_posted")
        if date_posted:
            try:
                if isinstance(date_posted, str):
                    posted_date = datetime.fromisoformat(date_posted)
                elif hasattr(date_posted, 'to_pydatetime'):
                    posted_date = date_posted.to_pydatetime()
            except Exception:
                pass

        # Determine source
        site = str(row.get("site", "JobSpy")) if row.get("site") else "JobSpy"
        source = f"JobSpy-{site.title()}"

        # Get direct application URL if available (this is the actual apply portal)
        # JobSpy provides job_url_direct for direct application links
        apply_url = None
        job_url_direct = row.get("job_url_direct")
        if job_url_direct and str(job_url_direct) not in ["", "nan", "None"]:
            apply_url = str(job_url_direct)

        return JobData(
            title=title,
            company=company,
            location=location,
            url=job_url,
            apply_url=apply_url,  # Direct application portal URL
            source=source,
            salary=salary,
            description=str(row.get("description", "")) if row.get("description") else None,
            posted_date=posted_date,
            is_startup=False,
        )
