# Stock Quote API

A small Flask backend for **David's Stock Lookup**. It returns live stock quotes, company info and key metrics, and powers a company-name autocomplete, all from the [Finnhub](https://finnhub.io) API.

This project follows the 'fetch data from an API that requires authentication' pattern: the backend holds the Finnhub API key as a Render environment variable and proxies requests, so the key is never exposed in frontend code.

- **Backend (Render):** https://stock-quote-api-t5yy.onrender.com
- **Frontend:** https://dcerrato-create.github.io/Personal-Website-Portfolio/stock-lookup/
- **Frontend repo:** https://github.com/dcerrato-create/Personal-Website-Portfolio (the page is [`stock-lookup/index.html`](https://github.com/dcerrato-create/Personal-Website-Portfolio/blob/main/stock-lookup/index.html))

**Coverage:** US stocks, ADRs and ETFs. Mutual funds aren't available on Finnhub's free plan, and indexes (like the S&P 500) aren't either, so the API points people to an ETF that tracks the index instead.

## 1. Endpoints

Every response is JSON. Every error is `{"error": "<message a person can read>"}` with a matching HTTP status, including unknown routes (404), wrong methods (405) and unexpected crashes (500).

### `POST /quote`

Returns a live quote plus company info and key metrics for one ticker.

**Request body (JSON):**

```json
{ "ticker": "AAPL" }
```

| Field    | Type   | Required | Notes |
|----------|--------|----------|-------|
| `ticker` | string | yes      | Case-insensitive, whitespace trimmed. Share classes can be written `BRK.B`, `BRK-B`, `BRK/B` or `BRK B`. |

**Success: `200 OK`**

```json
{
  "ticker": "AAPL",
  "type": "Stock",
  "name": "Apple Inc",
  "logo": "https://static2.finnhub.io/file/publicdatany/finnhubimage/stock_logo/AAPL.png",
  "price": 341.07,
  "change": 5.15,
  "change_percent": 1.5331,
  "as_of": "2026-09-25T20:00:00Z",
  "open": 336.04,
  "high": 341.67,
  "low": 334.53,
  "previous_close": 335.92,
  "week_52_high": 345.34,
  "week_52_low": 243.42,
  "pe_ratio": 38.6073,
  "market_cap": 4977637064987.0,
  "notes": []
}
```

| Field | Finnhub source | Meaning |
|---|---|---|
| `ticker` | request | Normalized symbol |
| `type` | `/stock/profile2` or `/search` | `"Stock"` (includes ADRs) or `"ETF"`; `null` if unknown |
| `name`, `logo` | `/stock/profile2` (ETFs: `/search`) | Company or fund name, logo URL |
| `price` | `/quote` | Last price (USD) |
| `change`, `change_percent` | `/quote` | $ and % change vs. the previous close |
| `as_of` | `/quote` | Time of the last price (ISO 8601, UTC). After hours and on weekends this is the last close. OTC stocks only get a date (midnight UTC). |
| `open`, `high`, `low`, `previous_close` | `/quote` | Session open, high and low, and the previous close |
| `week_52_high`, `week_52_low` | `/stock/metric` | 52-week range |
| `pe_ratio` | `/stock/metric` | Price/earnings ratio, trailing twelve months |
| `market_cap` | `/stock/profile2` | Market capitalization in USD (Finnhub reports millions; the backend converts to dollars) |
| `notes` | backend | Short explanations for any number that is missing or hidden (see below) |

The Finnhub quote call is required. The profile, metrics and search calls are optional: if they fail, the quote is still returned, the missing fields are `null`, and a note explains why.

**Notes the backend can send:**

| Situation | Note |
|---|---|
| ETF | P/E and market cap don't apply to ETFs. |
| ADR (Finnhub reports it in a non-USD currency) | 52-week range hidden, because Finnhub gives the home-market range in the local currency. Market cap hidden, because its currency isn't reliable (e.g. Alibaba's is in USD but labeled CNY). |
| Share class (e.g. BRK.B) | 52-week range hidden, because Finnhub returns another share class's range. |
| Company details unavailable | Only the price data is shown. |

**Errors:**

| Status | When | Example message |
|---|---|---|
| 400 | Body isn't a JSON object | `Send a JSON body like {"ticker": "AAPL"}.` |
| 400 | `ticker` isn't text | `The ticker must be text, like "AAPL".` |
| 400 | `ticker` missing or empty | `Please provide a ticker symbol.` |
| 400 | Not ticker-shaped (symbols, spaces, too long) | `That doesn't look like a ticker. Use letters and numbers, like AAPL or BRK.B.` |
| 404 | Unknown ticker (Finnhub price is 0) | `Ticker 'XYZXYZQ' not found. Tip: pick a company from the suggestions.` |
| 404 | An index (`^GSPC`, `S&P 500`, `^DJI`, ...) | `Indexes aren't available. Try SPY, an ETF that tracks the S&P 500.` |
| 404 | Not on Finnhub's free plan (e.g. mutual funds) | `That security isn't available on the free data plan (mutual funds, for example).` |
| 429 | Finnhub rate limit (60 calls/min) | `Too many requests to the data provider. Please wait a minute and try again.` |
| 500 | `FINNHUB_API_KEY` not set | `Server is missing FINNHUB_API_KEY.` |
| 502 | Finnhub unreachable or returned garbage | `Could not reach the stock data service.` |
| 502 | Finnhub rejected the API key | `The data provider rejected the server's API key.` |

### `GET /search?q=<text>`

Autocomplete: finds US stocks, ADRs and ETFs whose ticker or name matches `q`.

| Query param | Required | Notes |
|---|---|---|
| `q` | no | Partial ticker or company name, e.g. `AP`, `apple`, `spy`. Trimmed to 50 characters. |

**Success: `200 OK`**, a list of up to 6 matches:

```json
[
  { "symbol": "AAPL", "name": "Apple Inc", "type": "Stock" },
  { "symbol": "APLE", "name": "Apple Hospitality REIT Inc", "type": "Stock" }
]
```

- **Included:** Finnhub types "Common Stock" and "ADR" (labeled `Stock`) and "ETP" (labeled `ETF`).
- **Dotted symbols:** skipped because they're foreign listings, except share classes like `BRK.B`. When Finnhub returns only one class (e.g. BRK.A), the other one is added.
- **Built-in hints** (shown first, and still returned if Finnhub is down or rate-limited):
  - Index names suggest a tracking ETF: `s&p` → SPY, `dow` → DIA, `nasdaq` → QQQ, `russell` → IWM.
  - Well-known foreign companies suggest their US ticker, because Finnhub's name search misses many of them: `toyota` → TM, `tsmc` → TSM, `nestlé` → NSRGY. Accents are ignored.
- **Empty results:** empty or missing `q`, no matches, or a query Finnhub rejects (e.g. `c++`) all return `[]`.

**Errors:** `429` rate limit or `502` Finnhub unreachable (same messages as above), and `500` if the key is missing.

## 2. How the frontend uses it

The frontend is a single page in my portfolio repo on GitHub Pages. `BACKEND_URL` is a constant at the top of its script. There are three ways the page calls the backend:

1. **Autocomplete → `GET /search`**
   - As the user types, the page waits until they pause for 300 ms, then calls `/search?q=...`.
   - It shows a dropdown of `AAPL — Apple Inc` rows, each with a **Stock** or **ETF** badge.
   - Clicking a row, or choosing one with the arrow keys and Enter, requests a quote.
   - No results shows "No matches. Try the ticker instead, e.g. TM for Toyota."
   - An error shows the backend's message, like the rate-limit one.
   - Responses to older searches are ignored if a newer search has started.
2. **Get Quote button / Enter → `POST /quote`** with the typed ticker.
3. **Quick-pick buttons → `POST /quote`:** AAPL, NVDA, MSFT, TSLA and SPY each request a quote directly.

**While a quote is loading**, the page shows "Waking up server… (the first request can take up to a minute)", because Render's free tier sleeps when idle. The buttons are disabled so a request can't be sent twice.

**On `200`** the page renders a card with:
- the logo (or a letter badge), name and ticker, plus the Stock/ETF badge
- a large price
- the $/% change in green or red
- an "As of Fri, Sep 25, 4:00 PM ET · change vs. previous close" line, always shown in market time
- a grid: Open, Day High, Day Low, Prev Close, 52W High, 52W Low, P/E, Market Cap (`—` when `null`)
- the backend's `notes`, listed under the grid

Prices under $1 show up to 4 decimals.

**Errors:**
- `4xx`/`5xx` replies: the page shows the backend's `error` message.
- Replies that aren't JSON, like Render's HTML error page during a deploy: "Something went wrong (error 502)".
- A `200` reply without a price: "The server sent an unexpected response."
- No connection, or CORS blocked: "Couldn't reach the server…"
- No answer after 70 seconds: "The server took too long to respond."
- If two quotes are in flight, only the newest one updates the page.

All data is inserted with `textContent`, so HTML in a company name is shown as plain text, never run.

CORS is enabled with `flask-cors`, so the GitHub Pages origin (`https://dcerrato-create.github.io`) is allowed to call the Render backend, including the preflight check the browser sends before a JSON `POST`.

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
curl -X POST http://127.0.0.1:5001/quote -H "Content-Type: application/json" -d '{"ticker":""}'         # 400
curl -X POST http://127.0.0.1:5001/quote -H "Content-Type: application/json" -d '{"ticker":"XYZXYZQ"}'  # 404
curl "http://127.0.0.1:5001/search?q=apple"
```

To try the frontend against the local backend, temporarily set `BACKEND_URL` to `http://127.0.0.1:5001` in `stock-lookup/index.html` and open the file in a browser. Set it back to the Render URL before pushing.

### Environment variables

| Name              | Required | Description          |
|-------------------|----------|----------------------|
| `FINNHUB_API_KEY` | yes      | Your Finnhub API key |

### Deploying on Render

- **Instance type:** Free
- **Build command:** `pip install -r requirements.txt`
- **Start command:** `gunicorn app:app`
- **Environment:** add `FINNHUB_API_KEY` under the service's *Environment* tab

Render redeploys automatically on every push to `main`.

## 4. How secrets are handled

- The Finnhub key is read from the `FINNHUB_API_KEY` environment variable only. It is never hardcoded.
- **Locally**, `python-dotenv` loads it from a `.env` file. `.env` is listed in `.gitignore`, so it is never committed. `.env.example` shows the variable name with a placeholder value.
- **On Render**, the key is set as an environment variable in the dashboard.
- **The frontend never sees the key.** The browser only talks to `/quote` and `/search`, and the backend attaches the key when it calls Finnhub. Responses contain only stock data. The key never appears in responses or error messages.

## Prompt log

See [prompt_log.md](prompt_log.md).
