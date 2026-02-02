"""GitHub curated lists fetcher."""
import httpx
import re
from typing import List, Optional
from backend.models.job import JobData
from backend.config import settings


class GitHubFetcher:
    """Fetches jobs from GitHub curated internship lists."""

    # Canadian location keywords
    CANADIAN_LOCATIONS = [
        "toronto", "canada", "remote", "gta", "waterloo",
        "vancouver", "montreal", "ontario", "ottawa", "calgary"
    ]

    async def fetch_curated_jobs(self) -> List[JobData]:
        """
        Fetch jobs from all configured GitHub lists.

        Returns:
            List of JobData objects
        """
        all_jobs = []

        print(" GitHub: Starting to fetch curated lists...")

        for url in settings.github_list_urls:
            try:
                repo_name = "/".join(url.split("/")[3:5])
                print(f"   Fetching: {repo_name}")

                jobs = await self._fetch_from_url(url)
                print(f"   Found {len(jobs)} Canadian jobs from {repo_name}")
                all_jobs.extend(jobs)

            except Exception as e:
                print(f"   Error fetching {url}: {e}")

        print(f" GitHub: Total {len(all_jobs)} jobs from curated lists")
        return all_jobs

    async def _fetch_from_url(self, url: str) -> List[JobData]:
        """Fetch and parse a single GitHub markdown file."""
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                url,
                headers={"User-Agent": "TorontoJobTracker/1.0"}
            )

            if response.status_code == 404:
                print(f"   Repository not found (404)")
                return []

            if response.status_code != 200:
                print(f"   HTTP error: {response.status_code}")
                return []

            content = response.text
            return self._parse_markdown_table(content)

    def _parse_markdown_table(self, content: str) -> List[JobData]:
        """Parse markdown table to extract jobs."""
        jobs = []
        lines = content.split("\n")

        in_table = False
        header_parsed = False

        for line in lines:
            # Detect table start
            if "|" in line and not line.strip().startswith("<!--"):
                in_table = True

            if not in_table or "|" not in line:
                continue

            # Skip separator lines
            if "---" in line or ":--" in line or "--:" in line:
                header_parsed = True
                continue

            columns = [col.strip() for col in line.split("|") if col.strip()]

            if len(columns) < 2:
                continue

            # Skip header rows
            first_col = columns[0].lower()
            if any(kw in first_col for kw in ["company", "name", "organization"]):
                header_parsed = True
                continue

            if not header_parsed:
                continue

            # Extract company name
            company = self._extract_text(columns[0])

            # Skip empty or closed positions
            if not company or company == "↳" or "closed" in company.lower():
                continue

            # Try to determine title and location
            title = "Software Intern"
            location = ""

            for i, col in enumerate(columns[1:], 1):
                col_text = self._extract_text(col)
                col_lower = col_text.lower()

                # Check if location
                if any(loc in col_lower for loc in self.CANADIAN_LOCATIONS):
                    location = col_text

                # Check if job title
                elif any(kw in col_lower for kw in ["intern", "co-op", "engineer", "developer"]):
                    title = col_text

            # Check if Canadian location (in dedicated column or whole line)
            line_lower = line.lower()
            has_canadian = (
                any(loc in location.lower() for loc in self.CANADIAN_LOCATIONS) or
                any(loc in line_lower for loc in ["toronto", "canada", "🇨🇦"])
            )

            if not has_canadian:
                continue

            # Extract URL
            url = self._extract_url(line)
            if not url or url == "https://github.com":
                continue

            jobs.append(JobData(
                title=title,
                company=company,
                location=location if location else "Canada",
                url=url,
                source="GitHub",
                is_startup=False,
            ))

        return jobs

    def _extract_text(self, text: str) -> str:
        """Remove markdown formatting from text."""
        result = text

        # Remove markdown links [text](url) -> text
        result = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", result)

        # Remove images ![alt](url)
        result = re.sub(r"!\[[^\]]*\]\([^\)]+\)", "", result)

        # Remove formatting
        result = result.replace("**", "").replace("*", "").replace("`", "")

        # Remove emojis
        for emoji in ["✅", "❌", "🔒", "🇨🇦", "⬛"]:
            result = result.replace(emoji, "")

        return result.strip()

    def _extract_url(self, text: str) -> Optional[str]:
        """Extract URL from markdown link."""
        match = re.search(r"\]\(([^\)]+)\)", text)
        if match:
            url = match.group(1)
            if url.startswith("http"):
                return url
        return None
