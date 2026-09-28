import os
import re
import unicodedata
from datetime import datetime, timezone

import requests
from dotenv import load_dotenv
from flask import Flask, jsonify, request
from flask_cors import CORS

load_dotenv()  # reads .env locally; on Render the env var is set in the dashboard

FINNHUB_BASE = "https://finnhub.io/api/v1"
MAX_SEARCH_RESULTS = 6

# Finnhub security types we support, mapped to the label shown in the UI
SUPPORTED_TYPES = {"Common Stock": "Stock", "ADR": "Stock", "ETP": "ETF"}

# Share-class tickers like BRK.B or BF.B. Other dotted symbols are foreign listings.
SHARE_CLASS = re.compile(r"^[A-Z]+\.[A-Z]$")

# Finnhub's free plan has no index data, so point people to an ETF that tracks each index
INDEX_ETFS = {
    "s&p 500": ("SPY", "SPDR S&P 500 ETF Trust"),
    "dow jones": ("DIA", "SPDR Dow Jones Industrial Average ETF"),
    "nasdaq": ("QQQ", "Invesco QQQ Trust (Nasdaq-100)"),
    "russell 2000": ("IWM", "iShares Russell 2000 ETF"),
}
INDEX_SYMBOLS = {
    "^GSPC": "s&p 500", "^SPX": "s&p 500", "SPX": "s&p 500", "S&P 500": "s&p 500", "S&P500": "s&p 500",
    "^DJI": "dow jones", "DOW JONES": "dow jones",
    "^IXIC": "nasdaq", "^NDX": "nasdaq", "NDX": "nasdaq", "NASDAQ": "nasdaq",
    "^RUT": "russell 2000", "RUSSELL 2000": "russell 2000",
}
CLEAN_ETF_NAMES = {symbol: name for symbol, name in INDEX_ETFS.values()}

# Finnhub's name search misses many foreign companies' US listings (e.g. "toyota" finds only
# Tokyo's 7203.T, not the US ADR "TM"), so map well-known names to their US tickers
POPULAR_ADRS = {
    "toyota": ("TM", "Toyota Motor Corp (ADR)"),
    "honda": ("HMC", "Honda Motor Co (ADR)"),
    "taiwan semiconductor": ("TSM", "Taiwan Semiconductor Manufacturing (ADR)"),
    "tsmc": ("TSM", "Taiwan Semiconductor Manufacturing (ADR)"),
    "novo nordisk": ("NVO", "Novo Nordisk (ADR)"),
    "nestle": ("NSRGY", "Nestle SA (ADR)"),
    "shell": ("SHEL", "Shell plc (ADR)"),
    "unilever": ("UL", "Unilever plc (ADR)"),
    "astrazeneca": ("AZN", "AstraZeneca plc (ADR)"),
    "sanofi": ("SNY", "Sanofi (ADR)"),
    "nintendo": ("NTDOY", "Nintendo Co (ADR)"),
    "lvmh": ("LVMUY", "LVMH Moet Hennessy Louis Vuitton (ADR)"),
    "louis vuitton": ("LVMUY", "LVMH Moet Hennessy Louis Vuitton (ADR)"),
    "anheuser-busch": ("BUD", "Anheuser-Busch InBev (ADR)"),
    "budweiser": ("BUD", "Anheuser-Busch InBev (ADR)"),
    "rio tinto": ("RIO", "Rio Tinto plc (ADR)"),
    "diageo": ("DEO", "Diageo plc (ADR)"),
}

# Name hints shown at the top of search results: (keyword, symbol, display name, type)
SEARCH_HINTS = [(k, sym, name, "ETF") for k, (sym, name) in INDEX_ETFS.items()] + \
               [(k, sym, name, "Stock") for k, (sym, name) in POPULAR_ADRS.items()]

# Letters/digits with an optional share class (AAPL, BRK.B). Anything else is rejected before calling Finnhub.
VALID_TICKER = re.compile(r"^[A-Z0-9]{1,10}(\.[A-Z])?$")
MAX_SEARCH_LENGTH = 50

app = Flask(__name__)
CORS(app)


def finnhub_get(path, **params):
    """GET a Finnhub endpoint and return its JSON. Raises on network/HTTP errors."""
    params["token"] = os.environ["FINNHUB_API_KEY"]
    resp = requests.get(FINNHUB_BASE + path, params=params, timeout=10)
    resp.raise_for_status()
    return resp.json()


def finnhub_get_optional(path, **params):
    """Like finnhub_get, but returns {} on failure so extra data never breaks a quote."""
    try:
        return finnhub_get(path, **params) or {}
    except (requests.RequestException, ValueError):
        return {}


def missing_key_error():
    return jsonify({"error": "Server is missing FINNHUB_API_KEY."}), 500


def upstream_error(exc, service):
    """Turn a failed Finnhub call into a JSON error the frontend can show."""
    status = getattr(getattr(exc, "response", None), "status_code", None)
    if status == 429:
        return jsonify({"error": "Too many requests to the data provider. Please wait a minute and try again."}), 429
    if status == 401:
        return jsonify({"error": "The data provider rejected the server's API key."}), 502
    if status == 403:
        # Finnhub's free plan doesn't cover some securities, e.g. mutual funds like VFIAX
        return jsonify({"error": "That security isn't available on the free data plan (mutual funds, for example)."}), 404
    return jsonify({"error": f"Could not reach the {service}."}), 502


@app.route("/", methods=["GET"])
def index():
    """Opening the base URL in a browser shows that the API is up and how to use it."""
    return jsonify(
        {
            "service": "Stock Quote API",
            "status": "running",
            "endpoints": {
                "POST /quote": 'JSON body like {"ticker": "AAPL"}; returns a live quote, company info and key metrics',
                "GET /search?q=apple": "returns up to 6 matching US stocks, ADRs and ETFs",
            },
            "frontend": "https://dcerrato-create.github.io/Personal-Website-Portfolio/stock-lookup/",
        }
    )


# Every response is JSON, even for unknown routes, wrong methods or crashes
@app.errorhandler(404)
def not_found(_):
    return jsonify({"error": "Not found. Available endpoints: POST /quote and GET /search?q=..."}), 404


@app.errorhandler(405)
def method_not_allowed(_):
    return jsonify({"error": "Method not allowed. Use POST for /quote and GET for /search."}), 405


@app.errorhandler(500)
def server_error(_):
    return jsonify({"error": "Unexpected server error. Please try again."}), 500


def normalize_ticker(raw):
    """Uppercase and convert share-class spellings like BRK-B, BRK/B or BRK B to BRK.B."""
    ticker = str(raw).strip().upper()
    return re.sub(r"^([A-Z]+)[-/ ]([A-Z])$", r"\1.\2", ticker)


def index_error(ticker):
    """Friendly error for index symbols, pointing to an ETF that tracks the index."""
    key = INDEX_SYMBOLS.get(ticker)
    if key:
        etf, _ = INDEX_ETFS[key]
        message = f"Indexes aren't available. Try {etf}, an ETF that tracks the {key.title()}."
    else:
        message = "Indexes aren't available. Try an ETF that tracks one, like SPY for the S&P 500."
    return jsonify({"error": message}), 404


def find_listing(ticker):
    """Finnhub's search entry for an exact ticker ({} if none): gives the name and type (Common Stock, ADR, ETP)."""
    data = finnhub_get_optional("/search", q=ticker, exchange="US")
    return next((r for r in data.get("result") or [] if r.get("symbol") == ticker), {})


def week_range_note(ticker):
    """Explain why a (USD) 52-week range was hidden because it didn't match the price."""
    if SHARE_CLASS.match(ticker):
        return (f"52-week range hidden: for {ticker}, the data provider reports a different share class's "
                "range, which doesn't match this class's price.")
    return "52-week range hidden: the data provider's figures for this listing don't match its current price."




@app.route("/quote", methods=["POST"])
def quote():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": 'Send a JSON body like {"ticker": "AAPL"}.'}), 400
    raw = data.get("ticker")
    if raw is not None and not isinstance(raw, str):
        return jsonify({"error": "The ticker must be text, like \"AAPL\"."}), 400

    ticker = normalize_ticker(raw or "")
    if not ticker:
        return jsonify({"error": "Please provide a ticker symbol."}), 400

    if ticker.startswith("^") or ticker in INDEX_SYMBOLS:
        return index_error(ticker)

    if not VALID_TICKER.match(ticker):
        return jsonify({"error": "That doesn't look like a ticker. Use letters and numbers, like AAPL or BRK.B."}), 400

    if not os.environ.get("FINNHUB_API_KEY"):
        return missing_key_error()

    try:
        q = finnhub_get("/quote", symbol=ticker)
    except (requests.RequestException, ValueError) as exc:
        return upstream_error(exc, "stock data service")

    # Finnhub returns a current price of 0 (or null) for unknown tickers
    if not isinstance(q, dict) or not q.get("c"):
        return jsonify({"error": f"Ticker '{ticker}' not found. Tip: pick a company from the suggestions."}), 404

    profile = finnhub_get_optional("/stock/profile2", symbol=ticker)
    metrics = finnhub_get_optional("/stock/metric", symbol=ticker, metric="all").get("metric") or {}

    # ETFs have no company profile, so get their name and type from search instead
    if profile.get("name"):
        name, kind = profile["name"], "Stock"
    else:
        listing = find_listing(ticker)
        name, kind = listing.get("description"), SUPPORTED_TYPES.get(listing.get("type"))
    name = CLEAN_ETF_NAMES.get(ticker, name)

    notes = []
    week_high, week_low = metrics.get("52WeekHigh"), metrics.get("52WeekLow")
    # Finnhub reports market cap in millions, in the currency of the company's home market
    cap_millions = profile.get("marketCapitalization") or metrics.get("marketCapitalization")
    currency = profile.get("currency") or "USD"

    if currency != "USD":
        # ADRs: Finnhub gives home-market figures (e.g. yen), so the range can't sit next to a US dollar price.
        # Market cap is also hidden: its currency isn't reliable (Alibaba's is in USD but labeled CNY,
        # because "currency" is the company's filing currency, not the market cap's).
        if week_high:
            week_high = week_low = None
            notes.append(f"52-week range hidden: for ADRs, the data provider reports it in the home market's "
                         f"currency ({currency}), which doesn't match the US dollar price. This only affects ADRs.")
        if cap_millions:
            cap_millions = None
            notes.append("Market cap hidden: for ADRs, the data provider's figures aren't reliably in US dollars. "
                         "This only affects ADRs.")
    elif week_high and week_low and not (week_low * 0.5 <= q["c"] <= week_high * 2):
        # Finnhub sometimes returns another share class's range (BRK.B gets BRK.A's)
        week_high = week_low = None
        notes.append(week_range_note(ticker))

    if kind == "ETF":
        notes.append("P/E and market cap don't apply to ETFs.")
    if not name:
        notes.append("Company details are unavailable right now, so only the price data is shown.")

    # Time of the last trade (Finnhub gives Unix seconds); after hours and on weekends it's the last close
    as_of = datetime.fromtimestamp(q["t"], timezone.utc).isoformat().replace("+00:00", "Z") if q.get("t") else None

    return jsonify(
        {
            "ticker": ticker,
            "type": kind,
            "name": name or None,
            "logo": profile.get("logo") or None,
            "price": q["c"],
            "change": q.get("d"),
            "change_percent": q.get("dp"),
            "as_of": as_of,
            "open": q.get("o"),
            "high": q.get("h"),
            "low": q.get("l"),
            "previous_close": q.get("pc"),
            "week_52_high": week_high,
            "week_52_low": week_low,
            "pe_ratio": metrics.get("peTTM") or metrics.get("peBasicExclExtraTTM"),
            "market_cap": cap_millions * 1_000_000 if cap_millions else None,
            "notes": notes,
        }
    )


@app.route("/search", methods=["GET"])
def search():
    text = request.args.get("q", "").strip()[:MAX_SEARCH_LENGTH]
    if not text:
        return jsonify([])

    if not os.environ.get("FINNHUB_API_KEY"):
        return missing_key_error()

    matches = []

    # Typing an index name ("s&p") suggests its tracking ETF; a known foreign company ("toyota") its US ticker.
    # Accents are ignored so "nestlé" matches "nestle".
    lowered = unicodedata.normalize("NFKD", text.lower()).encode("ascii", "ignore").decode()
    if len(lowered) >= 3:
        for keyword, symbol, name, label in SEARCH_HINTS:
            if (keyword.startswith(lowered) or lowered.startswith(keyword)) and all(m["symbol"] != symbol for m in matches):
                matches.append({"symbol": symbol, "name": name, "type": label})

    try:
        data = finnhub_get("/search", q=text, exchange="US")
    except (requests.RequestException, ValueError) as exc:
        # Finnhub rejects some queries outright (e.g. "c++" gets 422), which just means no matches
        status = getattr(getattr(exc, "response", None), "status_code", None)
        if status in (400, 404, 422):
            return jsonify(matches)
        # The hints don't need Finnhub, so still return them if it's down or rate-limited
        return jsonify(matches) if matches else upstream_error(exc, "stock search service")
    if not isinstance(data, dict):
        data = {}

    for r in data.get("result") or []:
        symbol, label = r.get("symbol", ""), SUPPORTED_TYPES.get(r.get("type"))
        if not label or any(m["symbol"] == symbol for m in matches):
            continue
        # Dotted symbols are foreign listings unless they're share classes like BRK.B
        if "." in symbol and not SHARE_CLASS.match(symbol):
            continue
        name = CLEAN_ETF_NAMES.get(symbol, r.get("description", ""))
        matches.append({"symbol": symbol, "name": name, "type": label})

        # Finnhub search often returns only one share class (e.g. BRK.A), so look up its A/B sibling
        if SHARE_CLASS.match(symbol) and symbol[-1] in "AB":
            sibling = symbol[:-1] + ("B" if symbol[-1] == "A" else "A")
            found = finnhub_get_optional("/search", q=sibling, exchange="US").get("result", [])
            if any(x.get("symbol") == sibling for x in found) and all(m["symbol"] != sibling for m in matches):
                matches.append({"symbol": sibling, "name": f"{name} (Class {sibling[-1]})", "type": label})

    return jsonify(matches[:MAX_SEARCH_RESULTS])


if __name__ == "__main__":
    app.run(port=5001, debug=True)
