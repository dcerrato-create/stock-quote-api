import os

import requests
from dotenv import load_dotenv
from flask import Flask, jsonify, request
from flask_cors import CORS

load_dotenv()  # reads .env locally; on Render the env var is set in the dashboard

FINNHUB_URL = "https://finnhub.io/api/v1/quote"

app = Flask(__name__)
CORS(app)


@app.route("/quote", methods=["POST"])
def quote():
    data = request.get_json(silent=True) or {}
    ticker = str(data.get("ticker", "")).strip().upper()
    if not ticker:
        return jsonify({"error": "Please provide a ticker symbol."}), 400

    api_key = os.environ.get("FINNHUB_API_KEY")
    if not api_key:
        return jsonify({"error": "Server is missing FINNHUB_API_KEY."}), 500

    try:
        resp = requests.get(
            FINNHUB_URL, params={"symbol": ticker, "token": api_key}, timeout=10
        )
        resp.raise_for_status()
        result = resp.json()
    except requests.RequestException:
        return jsonify({"error": "Could not reach the stock data service."}), 502

    # Finnhub returns a current price of 0 for unknown tickers
    if not result.get("c"):
        return jsonify({"error": f"Ticker '{ticker}' not found."}), 404

    return jsonify(
        {"ticker": ticker, "price": result["c"], "change_percent": result.get("dp")}
    )


if __name__ == "__main__":
    app.run(port=5001, debug=True)
