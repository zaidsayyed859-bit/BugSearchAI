import requests

def check_security_headers(url):
    """
    Checks for common security headers on a given URL.
    Returns a structured report with present, missing, and weak headers.
    """
    report = {"present": {}, "missing": [], "weak": {}}

    try:
        response = requests.get(url, timeout=10, allow_redirects=True, headers={
            "User-Agent": "Mozilla/5.0"
        })

        # Expanded list of headers to check
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
                # Basic weakness checks
                if h == "X-Frame-Options" and value.lower() in ["allowall", ""]:
                    report["weak"][h] = value
                elif h == "Content-Security-Policy" and "unsafe-inline" in value.lower():
                    report["weak"][h] = value
                else:
                    report["present"][h] = value
            else:
                report["missing"].append(h)

    except requests.exceptions.RequestException as e:
        report["error"] = f"Request failed: {e}"

    return report


if __name__ == "__main__":
    import json
    url = "https://www.google.com"
    result = check_security_headers(url)
    print(json.dumps(result, indent=2))
