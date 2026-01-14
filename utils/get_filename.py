import re

import httpx


def get_filename_from_response(url):
    with httpx.stream("GET", url, follow_redirects=True) as response:
        response.raise_for_status()
        
        cd = response.headers.get("Content-Disposition")
        if cd:
            match = re.search(r'filename="?([^"]+)"?', cd)
            if match:
                return match.group(1)
        
        # fallback
        return "download.zip"
