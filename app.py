import os

import requests
from dotenv import load_dotenv
from flask import Flask, jsonify, request
from flask_cors import CORS

load_dotenv()  # reads .env locally; on Render the env var is set in the dashboard

FINNHUB_BASE = "https://finnhub.io/api/v1"
MAX_SEARCH_RESULTS = 6

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


@app.route("/quote", methods=["POST"])
def quote():
    data = request.get_json(silent=True) or {}
    ticker = str(data.get("ticker", "")).strip().upper()
    if not ticker:
        return jsonify({"error": "Please provide a ticker symbol."}), 400

    if not os.environ.get("FINNHUB_API_KEY"):
        return missing_key_error()

    try:
        q = finnhub_get("/quote", symbol=ticker)
    except (requests.RequestException, ValueError):
        return jsonify({"error": "Could not reach the stock data service."}), 502

    # Finnhub returns a current price of 0 for unknown tickers
    if not q.get("c"):
        return jsonify({"error": f"Ticker '{ticker}' not found."}), 404

    profile = finnhub_get_optional("/stock/profile2", symbol=ticker)
    metrics = finnhub_get_optional("/stock/metric", symbol=ticker, metric="all").get("metric") or {}

    # Finnhub reports market cap in millions of USD
    cap_millions = profile.get("marketCapitalization") or metrics.get("marketCapitalization")

    return jsonify(
        {
            "ticker": ticker,
            "name": profile.get("name") or None,
            "logo": profile.get("logo") or None,
            "price": q["c"],
            "change": q.get("d"),
            "change_percent": q.get("dp"),
            "open": q.get("o"),
            "high": q.get("h"),
            "low": q.get("l"),
            "previous_close": q.get("pc"),
            "week_52_high": metrics.get("52WeekHigh"),
            "week_52_low": metrics.get("52WeekLow"),
            "pe_ratio": metrics.get("peTTM") or metrics.get("peBasicExclExtraTTM"),
            "market_cap": cap_millions * 1_000_000 if cap_millions else None,
        }
    )


@app.route("/search", methods=["GET"])
def search():
    text = request.args.get("q", "").strip()
    if not text:
        return jsonify([])

    if not os.environ.get("FINNHUB_API_KEY"):
        return missing_key_error()

    try:
        data = finnhub_get("/search", q=text, exchange="US")
    except (requests.RequestException, ValueError):
        return jsonify({"error": "Could not reach the stock search service."}), 502

    # Keep US common stocks only; symbols with a "." are share classes or foreign listings
    matches = [
        {"symbol": r["symbol"], "name": r.get("description", "")}
        for r in data.get("result", [])
        if r.get("type") == "Common Stock" and "." not in r.get("symbol", ".")
    ]
    return jsonify(matches[:MAX_SEARCH_RESULTS])


if __name__ == "__main__":
    app.run(port=5001, debug=True)
