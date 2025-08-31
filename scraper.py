import re
import time
from typing import List
import requests
from bs4 import BeautifulSoup

HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; IranNewsBot/1.0; +https://example.com)"}
TIMEOUT = 20


def _fetch(url: str):
    r = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
    r.raise_for_status()
    return r.text


def _clean_titles(cands: List[str]) -> List[str]:
    out = []
    seen = set()
    for t in cands:
        t = re.sub(r"\s+", " ", t or "").strip()
        if not t:
            continue
        if len(t) < 4:
            continue
        key = t.lower()
        if key in seen:
            continue
        seen.add(key)
        out.append(t)
    return out


# 1) BBC Persian (صفحه اصلی)
# نمونه‌ها: https://www.bbc.com/persian  یا  https://www.bbc.com/persian/index.xml (RSS)

def get_bbc_persian(limit=4) -> List[str]:
    titles = []
    # تلاش اول: RSS
    try:
        rss = _fetch("https://www.bbc.com/persian/index.xml")
        soup = BeautifulSoup(rss, "xml")
        for item in soup.select("item > title"):
            titles.append(item.text)
            if len(titles) >= limit:
                return _clean_titles(titles)
    except Exception:
        pass

    # تلاش دوم: HTML صفحه اصلی
    try:
        html = _fetch("https://www.bbc.com/persian")
        soup = BeautifulSoup(html, "lxml")
        # عناوین معمولاً در h3/a قرار دارند
        for h in soup.find_all(["h3", "h2"]):
            t = h.get_text(" ", strip=True)
            if t:
                titles.append(t)
            if len(titles) >= limit:
                break
    except Exception:
        pass
    return _clean_titles(titles)[:limit]


# 2) Iran International (بخش ایران)

def get_iranintl(limit=4) -> List[str]:
    titles = []
    # اگر RSS نداشته باشه از HTML می‌خونیم
    try:
        html = _fetch("https://www.iranintl.com/iran")
        soup = BeautifulSoup(html, "lxml")
        for a in soup.select("a"):
            t = a.get_text(" ", strip=True)
            if t and 6 <= len(t) <= 140:
                titles.append(t)
            if len(titles) >= limit:
                break
    except Exception:
        pass
    # fallback: صفحه اصلی
    if len(_clean_titles(titles)) < limit:
        try:
            html = _fetch("https://www.iranintl.com/")
            soup = BeautifulSoup(html, "lxml")
            for h in soup.find_all(["h3", "h2"]):
                t = h.get_text(" ", strip=True)
                if t:
                    titles.append(t)
                if len(titles) >= limit:
                    break
        except Exception:
            pass
    return _clean_titles(titles)[:limit]


# 3) Reuters (Iran topic)

def get_reuters_iran(limit=4) -> List[str]:
    titles = []
    try:
        html = _fetch("https://www.reuters.com/world/middle-east/iran/")
        soup = BeautifulSoup(html, "lxml")
        # تیترها معمولاً در h3 و a ها هستند
        for h in soup.find_all(["h3", "h2"]):
            t = h.get_text(" ", strip=True)
            if t:
                titles.append(t)
            if len(titles) >= limit:
                break
    except Exception:
        pass
    return _clean_titles(titles)[:limit]


# 4) Radio Farda (TopNews ایران)

def get_radiofarda(limit=4) -> List[str]:
    titles = []
    try:
        html = _fetch("https://www.radiofarda.com/TopNews")
        soup = BeautifulSoup(html, "lxml")
        for a in soup.select("a"):
            t = a.get_text(" ", strip=True)
            if t and len(t) > 6:
                titles.append(t)
            if len(titles) >= limit:
                break
    except Exception:
        pass
    # fallback: تازه‌ترین‌ها
    if len(_clean_titles(titles)) < limit:
        try:
            html = _fetch("https://www.radiofarda.com/latestnews")
            soup = BeautifulSoup(html, "lxml")
            for h in soup.find_all(["h3", "h2"]):
                t = h.get_text(" ", strip=True)
                if t:
                    titles.append(t)
                if len(titles) >= limit:
                    break
        except Exception:
            pass
    return _clean_titles(titles)[:limit]


def get_latest_iran_headlines(limit=10) -> List[str]:
    """Round-robin از 4 منبع تا رسیدن به limit"""
    buckets = [
        get_iranintl(limit=5),
        get_bbc_persian(limit=5),
        get_reuters_iran(limit=5),
        get_radiofarda(limit=5),
    ]
    result = []
    i = 0
    # Round-robin
    while len(result) < limit and any(buckets):
        for b in buckets:
            if i < len(b):
                result.append(b[i])
                if len(result) >= limit:
                    break
        i += 1
    # اگر باز هم کم بود، باقیِ همه رو بریز تا پر شه
    if len(result) < limit:
        flat = []
        for b in buckets:
            flat.extend(b)
        result = _clean_titles(flat)[:limit]
    return result
