"""URL utilities for normalization and deduplication."""
from urllib.parse import urlparse, urlunparse, parse_qs, urlencode


# Tracking parameters to remove
TRACKING_PARAMS = ["utm_source", "utm_medium", "utm_campaign", "utm_content", "utm_term", "ref", "source", "fbclid", "gclid"]


def normalize_url(url: str) -> str:
    """
    Normalize a URL for deduplication.

    - Lowercase the URL
    - Remove tracking parameters
    - Remove trailing slashes

    Args:
        url: The URL to normalize

    Returns:
        Normalized URL string
    """
    if not url:
        return ""

    # Lowercase
    url = url.lower().strip()

    try:
        parsed = urlparse(url)

        # Parse query parameters and remove tracking ones
        query_params = parse_qs(parsed.query, keep_blank_values=False)
        filtered_params = {
            k: v for k, v in query_params.items() if k.lower() not in TRACKING_PARAMS
        }

        # Rebuild query string
        new_query = urlencode(filtered_params, doseq=True) if filtered_params else ""

        # Rebuild URL
        normalized = urlunparse(
            (
                parsed.scheme,
                parsed.netloc,
                parsed.path.rstrip("/"),  # Remove trailing slashes
                parsed.params,
                new_query,
                "",  # Remove fragment
            )
        )

        return normalized

    except Exception:
        # If parsing fails, just return lowercase URL without trailing slash
        return url.rstrip("/")


def extract_domain(url: str) -> str:
    """
    Extract the domain from a URL.

    Args:
        url: The URL to extract domain from

    Returns:
        Domain string (e.g., "example.com")
    """
    try:
        parsed = urlparse(url)
        return parsed.netloc.lower()
    except Exception:
        return ""
