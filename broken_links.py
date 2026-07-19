"""
broken_links.py

Module to find broken links on a webpage.
"""

import requests  # type: ignore
from urllib.parse import urljoin
from concurrent.futures import ThreadPoolExecutor


def check_link(full_url):
    """Check if a link is working or broken"""
    # Use User-Agent to avoid being treated as a crawler
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/114.0 Safari/537.36"
    }
    
    try:
        # Try HEAD first (faster)
        response = requests.head(full_url, timeout=5, allow_redirects=True, headers=headers)
        if response.status_code >= 400 or response.status_code == 405:
            # Fallback to GET if HEAD not allowed
            response = requests.get(full_url, timeout=5, allow_redirects=True, headers=headers)
        return full_url, response.status_code
    except requests.exceptions.RequestException as e:
        return full_url, f"Request Failed: {e}"


def check_broken_links(page, base_url):
    """Find all broken links on a webpage"""
    broken_links = []
    ok_links = []

    # Get all links
    links = page.query_selector_all("a")
    print(f"\nFound {len(links)} links.\n")

    urls = []
    for link in links:
        href = link.get_attribute("href")
        if not href or href.startswith(("javascript:", "mailto:", "#")):
            continue
        urls.append(urljoin(base_url, href))

    # Check links in parallel for speed
    with ThreadPoolExecutor(max_workers=10) as executor:
        results = executor.map(check_link, urls)

    # Sort results
    for full_url, status in results:
        if isinstance(status, int) and status < 400:
            ok_links.append({"url": full_url, "status": status})
            print(f"[OK] {status} -> {full_url}")
        else:
            broken_links.append({"url": full_url, "status": status})
            print(f"[BROKEN] {status} -> {full_url}")

    return {"ok_links": ok_links, "broken_links": broken_links}

