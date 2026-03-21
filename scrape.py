"""
Playwright script to scrape /r/wallstreetbets and count frequently mentioned stock tickers.

Requirements:
    pip install playwright
    playwright install chromium
"""

import asyncio
import re
from collections import Counter
from playwright.async_api import async_playwright

# ------------------------------------------------------------
# Known stock tickers (US equities).  Extend this list freely.
# We use an allowlist to avoid false-positives like "I", "A",
# "IT", "BY", "ON", "BE", etc. which appear in normal English.
# ------------------------------------------------------------
KNOWN_TICKERS = {
    "AAPL", "MSFT", "GOOGL", "GOOG", "AMZN", "META", "TSLA", "NVDA", "AMD",
    "INTC", "NFLX", "BABA", "DIS", "BA", "GE", "F", "GM", "PFE", "MRNA",
    "JNJ", "V", "MA", "JPM", "BAC", "WFC", "C", "GS", "MS", "XOM", "CVX",
    "COP", "SLB", "WMT", "COST", "TGT", "HD", "LOW", "AMGN", "GILD",
    "ABBV", "MRK", "LLY", "UNH", "CVS", "T", "VZ", "TMUS", "CMCSA",
    "NKLA", "RIVN", "LCID", "PLUG", "FCEL", "BLNK", "QQQ", "SPY", "IWM",
    "SQQQ", "TQQQ", "SPXU", "UVXY", "VIX", "GME", "AMC", "BB", "NOK",
    "BBBY", "PTON", "PLTR", "RBLX", "COIN", "HOOD", "SOFI", "UPST",
    "AFRM", "DKNG", "PENN", "MGM", "WYNN", "LVS", "CZR", "SNAP", "TWTR",
    "PINS", "SPOT", "UBER", "LYFT", "DASH", "ABNB", "AIRB", "DDOG",
    "SNOW", "CRWD", "ZS", "NET", "OKTA", "SPLK", "ESTC", "MDB", "PATH",
    "U", "UNITY", "TTD", "PUBM", "MGNI", "ROKU", "FUBO", "SIRI", "PARA",
    "WBD", "NWSA", "FOX", "FOXA", "LCNB", "NIO", "XPEV", "LI", "FSR",
    "RIDE", "GOEV", "WKHS", "SPCE", "ASTR", "RKLB", "MNTS", "ACHR",
    "JOBY", "LILM", "LAZR", "VLDR", "LIDR", "INVZ", "MVIS", "OUST",
    "CLF", "X", "NUE", "STLD", "MT", "AA", "FCX", "GOLD", "NEM", "KGC",
    "AEM", "WPM", "AG", "SLV", "GLD", "DXY", "TLT", "HYG", "LQD",
    "SOXL", "SOXS", "FNGU", "FNGD", "ARKK", "ARKW", "ARKG", "ARKF",
    "ARKX", "BITO", "MSTR", "MARA", "RIOT", "HUT", "BITF", "CLSK",
    "SQ", "PYPL", "SHOP", "ETSY", "EBAY", "MELI", "SE", "CPNG", "PDD",
    "JD", "BIDU", "TCEHY", "TME", "BILI", "IQ", "ZM", "DOCU", "BILL",
    "HUBS", "CRM", "NOW", "WDAY", "INTU", "ADBE", "ORCL", "SAP", "IBM",
    "CSCO", "QCOM", "TXN", "MU", "LRCX", "AMAT", "KLAC", "ASML", "TSM",
    "AVGO", "MCHP", "SWKS", "QRVO", "MPWR", "ON", "WOLF", "AAON",
    "NXPI", "STM", "IFNNY", "SMCI", "HPE", "HPQ", "DELL", "WDC", "STX",
    "PARA", "MOS", "CF", "NTR", "ADM", "BG", "DAL", "UAL", "AAL", "LUV",
    "JBLU", "ALK", "SAVE", "CCL", "RCL", "NCLH", "MAR", "HLT", "H",
}

# Regex that matches standalone uppercase word (potential ticker)
TICKER_RE = re.compile(r'\b([A-Z]{1,5})\b')

WSB_URL = "https://www.reddit.com/r/wallstreetbets/hot/"

# How many posts to scroll through (approximately)
SCROLL_ROUNDS = 6


async def scrape_wsb_tickers():
    ticker_counter: Counter = Counter()

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            )
        )
        page = await context.new_page()

        print(f"[*] Navigating to {WSB_URL} ...")
        await page.goto(WSB_URL, timeout=60_000, wait_until="domcontentloaded")

        # Allow lazy-loaded content to settle
        await page.wait_for_timeout(3000)

        for i in range(SCROLL_ROUNDS):
            print(f"[*] Scroll round {i + 1}/{SCROLL_ROUNDS} ...")
            await page.evaluate("window.scrollBy(0, window.innerHeight * 3)")
            await page.wait_for_timeout(2000)

        # ---- Gather post titles ----
        # Reddit renders posts in <shreddit-post> custom elements (new Reddit)
        # Fall back to link text if that selector doesn't match.
        titles = await page.evaluate("""
            () => {
                let texts = [];
                // New Reddit (shreddit)
                document.querySelectorAll('shreddit-post').forEach(el => {
                    const t = el.getAttribute('post-title') || el.getAttribute('aria-label') || '';
                    if (t) texts.push(t);
                });
                // Old/fallback selectors
                if (texts.length === 0) {
                    document.querySelectorAll('h3, [data-testid="post-content"] h3, .Post h3').forEach(el => {
                        texts.push(el.innerText);
                    });
                }
                // Also grab visible text of post-title anchors
                document.querySelectorAll('a[slot="title"], a[data-click-id="body"]').forEach(el => {
                    texts.push(el.innerText);
                });
                return texts;
            }
        """)

        print(f"[*] Collected {len(titles)} post titles. Counting tickers...\n")

        for title in titles:
            for match in TICKER_RE.finditer(title):
                ticker = match.group(1)
                if ticker in KNOWN_TICKERS:
                    ticker_counter[ticker] += 1

        await browser.close()

    return ticker_counter


def main():
    counter = asyncio.run(scrape_wsb_tickers())

    if not counter:
        print("No known tickers found. The page layout may have changed.")
        print("Try increasing SCROLL_ROUNDS or inspecting the page manually.")
        return

    print("=" * 40)
    print(f"{'Ticker':<10} {'Mentions':>8}")
    print("=" * 40)
    for ticker, count in counter.most_common(25):
        bar = "█" * min(count * 2, 30)
        print(f"{ticker:<10} {count:>8}  {bar}")
    print("=" * 40)
    print(f"Total unique tickers found: {len(counter)}")


if __name__ == "__main__":
    main()
