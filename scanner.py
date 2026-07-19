"""
Scanner.py

Main module that combines all scanning functions:
- Console errors
- Broken links
- Missing/broken images
- Security headers
"""

from playwright.sync_api import sync_playwright
from broken_links import check_broken_links
from missing_images import check_missing_images
from security_headers import check_security_headers


def scan_website(url):
    """Comprehensive website scanner"""
    console_errors = []
    broken_links_report = {}
    images_report = {}
    security_report = {}

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # Capture console errors
        def handle_console(msg):
            if msg.type == "error":
                console_errors.append(msg.text)

        page.on("console", handle_console)
        page.goto(url, wait_until="load", timeout=60000)

        # Run broken link check
        broken_links_report = check_broken_links(page, url)

        # Run missing image check
        images_report = check_missing_images(page, url)

        page.wait_for_timeout(3000)
        page.close()
        browser.close()

    # Check security headers (outside playwright context)
    security_report = check_security_headers(url)

    return {
        "url": url,
        "console_errors": console_errors,
        "broken_links": broken_links_report["broken_links"],
        "ok_links": broken_links_report["ok_links"],
        "broken_images": images_report["broken_images"],
        "ok_images": images_report["ok_images"],
        "security_headers": security_report
    }


if __name__ == "__main__":
    import json
    url = "https://example.com"
    result = scan_website(url)
    print(json.dumps(result, indent=2))

