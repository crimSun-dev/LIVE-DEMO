"""Build only public frontend files; never copy backend settings or credentials."""
import json
import os
from pathlib import Path
import shutil
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]


def build():
    api_base = os.environ.get("API_BASE_URL", "").strip().rstrip("/")
    if api_base:
        url = urlsplit(api_base)
        if url.scheme != "https" or not url.hostname or url.username or url.password or url.query or url.fragment:
            raise ValueError("API_BASE_URL must be a public HTTPS backend URL without credentials, query, or fragment")
    target = ROOT / "_site"
    target.mkdir(exist_ok=True)
    shutil.copyfile(ROOT / "backend/app/static/index.html", target / "index.html")
    (target / "config.js").write_text("window.DW_API_BASE = " + json.dumps(api_base) + ";\n", encoding="utf-8")
    (target / ".nojekyll").touch()


if __name__ == "__main__":
    build()
