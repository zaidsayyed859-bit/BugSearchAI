from playwright.sync_api import sync_playwright

def scan_website(url):
    """
    Opens a website, captures JavaScript console errors,
    and simulates basic interactions.
    """
    console_errors = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # Listen for console messages
        def handle_console(msg):
            if msg.type == "error":
                console_errors.append(msg.text)

        page.on("console", handle_console)

        # Load the page with timeout
        page.goto(url, wait_until="load", timeout=60000)

        # Example interaction: click a button if present
        if page.query_selector("button"):
            try:
                page.click("button")
            except Exception as e:
                console_errors.append(f"Interaction error: {e}")

        # Keep page alive longer to catch delayed errors
        page.wait_for_timeout(5000)

        page.close()
        browser.close()

    return {
        "url": url,
        "console_errors": console_errors
    }


if __name__ == "__main__":
    url = "https://evplanet.in/"
    result = scan_website(url)
    print(result)
