"""URL resolver utility for finding direct application portal URLs."""
import asyncio
import re
import httpx
from typing import List, Optional
from backend.models.job import JobData


# Application portal domains we're looking for
APPLICATION_PORTALS = [
    "workday.com",
    "myworkdayjobs.com",
    "greenhouse.io",
    "lever.co",
    "ashbyhq.com",
    "bamboohr.com",
    "smartrecruiters.com",
    "icims.com",
    "jobvite.com",
    "taleo.net",
    "brassring.com",
    "ultipro.com",
    "successfactors.com",
    "applicantpro.com",
    "paylocity.com",
    "recruiting.adp.com",
    "jobs.lever.co",
    "boards.greenhouse.io",
    "careers.smartrecruiters.com",
    "oraclecloud.com",
    "csod.com",  # Cornerstone
    "phenom.com",
    "recruitingsite.com",
    "applytojob.com",
]


def extract_apply_url_from_html(html: str, base_url: str) -> Optional[str]:
    """
    Extract application portal URL from page HTML content.
    Looks for links to known application portals.
    """
    # Look for links to application portals in the HTML
    # Pattern matches href="..." containing portal domains
    for portal in APPLICATION_PORTALS:
        # Match href attributes containing the portal domain
        patterns = [
            rf'href=["\']([^"\']*{re.escape(portal)}[^"\']*)["\']',
            rf'data-href=["\']([^"\']*{re.escape(portal)}[^"\']*)["\']',
            rf'action=["\']([^"\']*{re.escape(portal)}[^"\']*)["\']',
        ]
        for pattern in patterns:
            match = re.search(pattern, html, re.IGNORECASE)
            if match:
                url = match.group(1)
                # Handle relative URLs
                if url.startswith('/'):
                    from urllib.parse import urljoin
                    url = urljoin(base_url, url)
                # Filter out tracking/analytics URLs
                if 'click' not in url.lower() and 'track' not in url.lower():
                    return url
    return None


async def resolve_apply_url(listing_url: str, timeout: float = 10.0) -> str:
    """
    Follow redirects from a job board listing to find the actual application portal URL.
    If redirects don't lead to a portal, try to extract the apply link from the page.

    Args:
        listing_url: The job board listing URL (Indeed, LinkedIn, etc.)
        timeout: Request timeout in seconds

    Returns:
        The final destination URL after following redirects, or original URL if resolution fails
    """
    if not listing_url:
        return listing_url

    try:
        async with httpx.AsyncClient(
            follow_redirects=True,
            timeout=timeout,
            # Some sites block without a proper User-Agent
            headers={
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            }
        ) as client:
            # Use GET request to get page content
            response = await client.get(listing_url)
            final_url = str(response.url)

            # Check if we landed on an application portal via redirect
            if is_application_portal(final_url):
                print(f"      ✓ Resolved to portal: {_truncate_url(final_url)}")
                return final_url

            # Try to extract apply URL from page content
            html = response.text
            extracted_url = extract_apply_url_from_html(html, final_url)
            if extracted_url:
                print(f"      ✓ Extracted portal link: {_truncate_url(extracted_url)}")
                return extracted_url

            # If not an application portal, return original
            return listing_url

    except httpx.TimeoutException:
        print(f"      ⚠ Timeout resolving: {_truncate_url(listing_url)}")
        return listing_url
    except Exception as e:
        # If anything fails, return original URL
        print(f"      ⚠ Failed to resolve: {_truncate_url(listing_url)} ({type(e).__name__})")
        return listing_url


def is_application_portal(url: str) -> bool:
    """Check if URL is from a known application portal."""
    url_lower = url.lower()
    return any(portal in url_lower for portal in APPLICATION_PORTALS)


def _truncate_url(url: str, max_length: int = 60) -> str:
    """Truncate URL for logging."""
    if len(url) <= max_length:
        return url
    return url[:max_length - 3] + "..."


async def resolve_jobs_urls(jobs: List[JobData], batch_size: int = 10) -> List[JobData]:
    """
    Resolve apply URLs for a list of jobs concurrently.

    Args:
        jobs: List of JobData objects to process
        batch_size: Number of concurrent URL resolutions

    Returns:
        Same jobs list with apply_url populated where resolved
    """
    if not jobs:
        return jobs

    # Count how many already have apply_url (e.g., from JobSpy's job_url_direct)
    already_have_url = sum(1 for job in jobs if job.apply_url)
    need_resolution = [job for job in jobs if not job.apply_url]

    print(f"   🔗 {already_have_url} jobs already have direct apply URLs")
    print(f"   🔗 Resolving application URLs for {len(need_resolution)} remaining jobs...")

    if not need_resolution:
        return jobs

    # Process in batches to avoid overwhelming servers
    resolved_count = 0

    for i in range(0, len(need_resolution), batch_size):
        batch = need_resolution[i:i + batch_size]

        # Create resolution tasks for this batch
        tasks = [resolve_apply_url(job.url) for job in batch]

        # Wait for all resolutions in this batch
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Update jobs with resolved URLs
        for job, result in zip(batch, results):
            if isinstance(result, str) and result != job.url:
                job.apply_url = result
                resolved_count += 1

        # Small delay between batches
        if i + batch_size < len(need_resolution):
            await asyncio.sleep(0.5)

    total_with_apply_url = already_have_url + resolved_count
    print(f"   🔗 Total jobs with direct apply URLs: {total_with_apply_url}/{len(jobs)}")

    return jobs
