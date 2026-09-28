# Stock Quote API

A small Flask backend for **David's Stock Lookup**. It looks up live stock quotes, company info and key metrics, and powers a company-name autocomplete, all from the [Finnhub](https://finnhub.io) API.

This project follows the 'fetch data from an API that requires authentication' pattern: the backend holds the Finnhub API key as a Render environment variable and proxies requests, so the key is never exposed in frontend code.

- **Backend (Render):** https://stock-quote-api-t5yy.onrender.com
- **Frontend:** https://dcerrato-create.github.io/Personal-Website-Portfolio/stock-lookup/
- **Frontend repo:** https://github.com/dcerrato-create/Personal-Website-Portfolio

## 1. Endpoints

### `POST /quote`

Returns a live quote plus company info and key metrics for one ticker.

**Request body (JSON):**

```json
{ "ticker": "AAPL" }
```

| Field    | Type   | Required | Notes                                                 |
|----------|--------|----------|-------------------------------------------------------|
| `ticker` | string | yes      | Stock symbol. Case-insensitive, whitespace is trimmed. |

**Success: `200 OK`**

```json
{
  "ticker": "AAPL",
  "name": "Apple Inc",
  "logo": "https://static2.finnhub.io/file/publicdatany/finnhubimage/stock_logo/AAPL.png",
  "price": 341.07,
  "change": 5.15,
  "change_percent": 1.5331,
  "open": 336.04,
  "high": 341.67,
  "low": 334.53,
  "previous_close": 335.92,
  "week_52_high": 345.34,
  "week_52_low": 243.42,
  "pe_ratio": 38.6073,
  "market_cap": 4977637064987.0
}
```

| Field | Source (Finnhub) | Meaning |
|---|---|---|
| `ticker` | request | Normalized symbol |
| `name`, `logo` | `/stock/profile2` | Company name and logo URL |
| `price` | `/quote` | Current price (USD) |
| `change`, `change_percent` | `/quote` | $ and % change since the previous close |
| `open`, `high`, `low`, `previous_close` | `/quote` | Today's open, high and low, and yesterday's close |
| `week_52_high`, `week_52_low` | `/stock/metric` | 52-week range |
| `pe_ratio` | `/stock/metric` | Price/earnings ratio, trailing twelve months |
| `market_cap` | `/stock/profile2` | Market capitalization in USD (Finnhub reports millions; the backend converts it to dollars) |

The quote is required. The profile and metrics are optional: if either of those Finnhub calls fails, the quote is still returned, and the missing fields are `null`.

**Errors** (every error comes back as JSON with an `error` message):

| Status | When                                    | Example body                                   |
|--------|-----------------------------------------|------------------------------------------------|
| 400    | `ticker` is missing or empty            | `{"error": "Please provide a ticker symbol."}` |
| 404    | Finnhub doesn't know the ticker (it returns a price of 0) | `{"error": "Ticker 'XYZXYZQ' not found."}` |
| 500    | `FINNHUB_API_KEY` is not set on the server | `{"error": "Server is missing FINNHUB_API_KEY."}` |
| 502    | The Finnhub quote call failed           | `{"error": "Could not reach the stock data service."}` |

### `GET /search?q=<text>`

Autocomplete: finds US common stocks whose ticker or name matches `q`.

| Query param | Required | Notes |
|---|---|---|
| `q` | no | Partial ticker or company name, e.g. `AP` or `apple` |

**Success: `200 OK`**, a list of up to 6 matches:

```json
[
  { "symbol": "AAPL", "name": "Apple Inc" },
  { "symbol": "APLE", "name": "Apple Hospitality REIT Inc" }
]
```

- Only results with type "Common Stock" are returned. Symbols containing a `.` are skipped, because they are share classes or foreign listings.
- An empty or missing `q` returns `[]`. A search with no matches also returns `[]`.

**Errors:** `500` if the API key is missing. `502` `{"error": "Could not reach the stock search service."}` if Finnhub fails.

## 2. How the frontend uses it

The frontend is a single page, [`stock-lookup/index.html`](https://github.com/dcerrato-create/Personal-Website-Portfolio/tree/main/stock-lookup), in my portfolio repo on GitHub Pages. `BACKEND_URL` is a constant at the top of its script.

- **Autocomplete → `GET /search`:** as the user types, the page waits until they pause for 300 ms, then calls `/search?q=...`. It shows the matches as a dropdown of "AAPL — Apple Inc" rows, or "No matches." if there are none. Clicking a row, or picking one with the arrow keys and Enter, fills the input and requests a quote.
- **Quote → `POST /quote`:** runs when the user clicks **Get Quote**, picks a suggestion, or clicks a quick-pick button (AAPL, NVDA, MSFT, TSLA). The page shows a "Waking up server…" note while waiting, because Render's free tier sleeps when idle and the first request can take up to about a minute. On `200` it renders a card with:
  - the logo and company name
  - a large price
  - the $/% change in green or red
  - a grid with Open, Day High, Day Low, Prev Close, 52W High, 52W Low, P/E and Market Cap
- **Errors:** on `400`/`404`/`5xx` the page shows the backend's `error` message. If the request can't connect at all (backend down), it shows a friendly "couldn't reach the server" message instead.

CORS is enabled with `flask-cors`, so the GitHub Pages site (a different origin) is allowed to call the Render backend.

## 3. Running locally

Requires Python 3.9+.

```bash
git clone https://github.com/dcerrato-create/stock-quote-api.git
cd stock-quote-api
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# edit .env and set FINNHUB_API_KEY to your key (free at https://finnhub.io/register)

python app.py
```

The server runs at `http://127.0.0.1:5001`. It uses port 5001 because macOS AirPlay Receiver takes port 5000.

Test it:

```bash
curl -X POST http://127.0.0.1:5001/quote -H "Content-Type: application/json" -d '{"ticker":"AAPL"}'
curl "http://127.0.0.1:5001/search?q=apple"
```

To try the frontend against the local backend, temporarily set `BACKEND_URL` to `http://127.0.0.1:5001` in `stock-lookup/index.html` and open the file in a browser.

### Environment variables

| Name              | Required | Description          |
|-------------------|----------|----------------------|
| `FINNHUB_API_KEY` | yes      | Your Finnhub API key |

### Deploying on Render

- **Build command:** `pip install -r requirements.txt`
- **Start command:** `gunicorn app:app`
- **Environment:** add `FINNHUB_API_KEY` under the service's *Environment* tab

## 4. How secrets are handled

- The Finnhub key is read from the `FINNHUB_API_KEY` environment variable only. It is never hardcoded.
- **Locally**, `python-dotenv` loads it from a `.env` file. `.env` is listed in `.gitignore`, so it is never committed. `.env.example` shows the variable name with a placeholder value.
- **On Render**, the key is set as an environment variable in the dashboard.
- **The frontend never sees the key.** The browser only talks to `/quote` and `/search`, and the backend attaches the key when it calls Finnhub. Responses contain only the stock data, never the key.

## Prompt log

See [prompt_log.md](prompt_log.md).
