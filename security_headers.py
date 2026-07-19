"""
security_headers.py

Module to check for security headers on a webpage.
"""

import requests  # type: ignore


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

