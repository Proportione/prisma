"""Unpaywall API client for legal open-access PDF discovery.

Requires a polite email. Free, no API key.
https://unpaywall.org/products/api
"""
from __future__ import annotations

import time

import requests

UNPAYWALL_BASE = "https://api.unpaywall.org/v2"


def unpaywall_lookup(doi: str, email: str, timeout: float = 15.0) -> dict | None:
    """Return the Unpaywall payload for a DOI, or None if not found."""
    if not doi:
        return None
    url = f"{UNPAYWALL_BASE}/{doi}"
    r = requests.get(url, params={"email": email}, timeout=timeout)
    if r.status_code == 404:
        return None
    r.raise_for_status()
    return r.json()


def best_oa_pdf_url(payload: dict) -> str | None:
    """Extract the best open-access PDF URL from an Unpaywall payload."""
    if not payload:
        return None
    best = payload.get("best_oa_location") or {}
    return best.get("url_for_pdf") or best.get("url") or None


def download_pdf(url: str, output_path: str, timeout: float = 60.0) -> bool:
    """Download a PDF if the response is application/pdf. Returns success."""
    r = requests.get(url, timeout=timeout, stream=True, headers={"User-Agent": "PRISMA-toolkit"})
    if r.status_code != 200 or "pdf" not in r.headers.get("Content-Type", "").lower():
        return False
    with open(output_path, "wb") as f:
        for chunk in r.iter_content(chunk_size=65536):
            if chunk:
                f.write(chunk)
    return True


def batch_download(
    dois_and_paths: list[tuple[str, str]],
    email: str,
    sleep: float = 0.5,
) -> list[dict]:
    """Try to download a list of DOIs to local paths.

    Returns a list of `{doi, ok, url, path}` dicts for the audit trail.
    """
    results = []
    for doi, path in dois_and_paths:
        payload = unpaywall_lookup(doi, email=email)
        url = best_oa_pdf_url(payload) if payload else None
        ok = bool(url) and download_pdf(url, path) if url else False
        results.append({"doi": doi, "ok": ok, "url": url, "path": path})
        time.sleep(sleep)
    return results
