"""
missing_images.py

Module to find missing or broken images on a webpage.
"""

from urllib.parse import urljoin
from concurrent.futures import ThreadPoolExecutor
from broken_links import check_link


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
