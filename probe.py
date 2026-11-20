"""Can a GitHub Actions runner reach each data source? Prints one verdict line per site."""
import sys, time
from curl_cffi import requests as cr

def plain(name, url):
    try:
        r = cr.get(url, impersonate="chrome", timeout=40)
        cf = "just a moment" in r.text.lower() or r.status_code in (403, 429, 503)
        print(f"[PROBE] {name:8} HTTP {r.status_code} len={len(r.text)} {'BLOCKED' if cf else 'OK'}  {url}")
    except Exception as e:
        print(f"[PROBE] {name:8} ERROR {type(e).__name__}: {str(e)[:100]}  {url}")

plain("NJCAA", "https://0wtr7r0cl7.execute-api.us-east-2.amazonaws.com/prod")
plain("NJCAA-w", "https://www.njcaa.org/")
plain("NCAA-www", "https://www.ncaa.com/")
plain("NCAA-api", "https://sdataprod.ncaa.com/")
plain("NCCAA", "https://thenccaa.org/")

from playwright.sync_api import sync_playwright
def browser(name, url):
    with sync_playwright() as p:
        b = p.chromium.launch(channel="chrome", headless=False, args=["--no-sandbox"])
        pg = b.new_page()
        try:
            resp = pg.goto(url, wait_until="domcontentloaded", timeout=60000)
            st = resp.status if resp else None
            for i in range(12):                     # give the Cloudflare JS check 60s to self-pass
                t = pg.title()
                if "just a moment" not in t.lower():
                    break
                time.sleep(5)
            t = pg.title()
            blocked = "just a moment" in t.lower() or st in (403, 429)
            print(f"[PROBE] {name:8} HTTP {st} title={t[:60]!r} {'BLOCKED' if blocked else 'OK'}  {url}")
        except Exception as e:
            print(f"[PROBE] {name:8} ERROR {type(e).__name__}: {str(e)[:100]}  {url}")
        b.close()

browser("NAIA", "https://naiastats.prestosports.com/sports/mbkb/2026-27/teams")
browser("NWAC", "https://nwac.prestosports.com/sports/mbkb/2026-27/teams")
