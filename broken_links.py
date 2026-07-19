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


def check_missing_images(page, base_url):
    """Find all broken or missing images on a webpage"""
    broken_images = []
    ok_images = []

    # Get all images
    images = page.query_selector_all("img")
    print(f"\nFound {len(images)} images.\n")

    image_urls = []
    for img in images:
        src = img.get_attribute("src")
        alt = img.get_attribute("alt")
        
        if not src:
            broken_images.append({"url": "No src", "alt": alt or "No alt text"})
            print(f"[BROKEN] No src attribute - alt: {alt}")
            continue
        
        full_url = urljoin(base_url, src)
        image_urls.append((full_url, alt))

    # Check images in parallel
    with ThreadPoolExecutor(max_workers=10) as executor:
        results = executor.map(check_link, [url for url, _ in image_urls])

    # Map results back to images with their alt text
    for (full_url, alt), (_, status) in zip(image_urls, results):
        if isinstance(status, int) and status < 400:
            ok_images.append({"url": full_url, "status": status, "alt": alt})
            print(f"[OK] {status} -> {full_url}")
        else:
            broken_images.append({"url": full_url, "status": status, "alt": alt})
            print(f"[BROKEN] {status} -> {full_url}")

    return {"ok_images": ok_images, "broken_images": broken_images}


def check_security_headers(url):
    """Check for common security headers on a given URL"""
    headers_to_check = {
        "present": {},
        "missing": [],
        "weak": {}
    }

    try:
        response = requests.get(url, timeout=10, allow_redirects=True, headers={
            "User-Agent": "Mozilla/5.0"
        })

        security_headers = [
            "Content-Security-Policy",
            "Strict-Transport-Security",
            "X-Frame-Options",
            "X-Content-Type-Options",
            "Referrer-Policy",
            "Permissions-Policy",
            "Cross-Origin-Resource-Policy",
            "Cross-Origin-Opener-Policy",
            "Cross-Origin-Embedder-Policy"
        ]

        for h in security_headers:
            value = response.headers.get(h)
            if value:
                # Check for weak configurations
                if h == "X-Frame-Options" and value.lower() in ["allowall", ""]:
                    headers_to_check["weak"][h] = value
                elif h == "Content-Security-Policy" and "unsafe-inline" in value.lower():
                    headers_to_check["weak"][h] = value
                else:
                    headers_to_check["present"][h] = value
            else:
                headers_to_check["missing"].append(h)

    except requests.exceptions.RequestException as e:
        headers_to_check["error"] = f"Request failed: {e}"

    return headers_to_check
