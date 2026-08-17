#!/usr/bin/env python3
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parent.parent / "static" / "fonts"
ROOT.mkdir(parents=True, exist_ok=True)
FILES = {
    "source-serif-4.woff2": "https://fonts.gstatic.com/s/sourceserif4/v14/vEFI2_tTDB4M7-auWDN0ahZJW1gb8tc.woff2",
    "source-sans-3.woff2": "https://fonts.gstatic.com/s/sourcesans3/v19/nwpStKy2OAdR1K-IwhWudF-R3w8aZQ.woff2",
    "cairo.woff2": "https://fonts.gstatic.com/s/cairo/v31/SLXVc1nY6HkvangtZmpQdkhzfH5lkSscQyyS4J0.woff2",
}

for name, url in FILES.items():
    dest = ROOT / name
    req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urlopen(req, timeout=30) as response:
        dest.write_bytes(response.read())
    print(f"{name} {dest.stat().st_size}")
