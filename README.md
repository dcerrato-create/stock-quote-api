# Stock Quote API

A small Flask backend that looks up the current price of a stock. It calls the [Finnhub](https://finnhub.io) quote API on the server, so the Finnhub API key never reaches the browser.

- **Backend (Render):** https://stock-quote-api-t5yy.onrender.com
- **Frontend:** https://dcerrato-create.github.io/Personal-Website-Portfolio/stock-lookup/
- **Frontend repo:** https://github.com/dcerrato-create/Personal-Website-Portfolio

## 1. Endpoint

### `POST /quote`

**Request body (JSON):**

```json
{ "ticker": "AAPL" }
```

| Field    | Type   | Required | Notes                                        |
|----------|--------|----------|----------------------------------------------|
| `ticker` | string | yes      | Stock symbol. Case-insensitive, whitespace is trimmed. |

**Success: `200 OK`**

```json
{ "ticker": "AAPL", "price": 227.52, "change_percent": 1.34 }
```

- `price`: current price in USD
- `change_percent`: percent change since the previous close

**Errors** (every error comes back as JSON with an `error` message):

| Status | When                                    | Example body                                   |
|--------|-----------------------------------------|------------------------------------------------|
| 400    | `ticker` is missing or empty            | `{"error": "Please provide a ticker symbol."}` |
| 404    | Finnhub doesn't know the ticker (it returns a price of 0) | `{"error": "Ticker 'XYZXYZ' not found."}` |
| 500    | `FINNHUB_API_KEY` is not set on the server | `{"error": "Server is missing FINNHUB_API_KEY."}` |
| 502    | Finnhub could not be reached or returned an error | `{"error": "Could not reach the stock data service."}` |

## 2. How the frontend uses it

The frontend is a single page, [`stock-lookup/index.html`](https://github.com/dcerrato-create/Personal-Website-Portfolio/tree/main/stock-lookup), in my portfolio repo on GitHub Pages.

1. The user types a ticker and clicks **Get Quote**.
2. The page shows a "waking up server…" note, because Render's free tier sleeps when idle and the first request can take up to about a minute.
3. It sends `fetch(BACKEND_URL + "/quote", { method: "POST", headers: {"Content-Type": "application/json"}, body: JSON.stringify({ticker}) })`. `BACKEND_URL` is a constant at the top of the script.
4. On `200`, it displays the ticker, the price, and the percent change.
5. On `400`/`404`/`5xx`, it displays the `error` message from the JSON body. If the request can't connect at all (backend down or asleep and timing out), it displays a friendly "couldn't reach the server" message.

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
```

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
- **The frontend never sees the key.** The browser only talks to `/quote`, and the backend attaches the key when it calls Finnhub. The response contains only the ticker, price, and percent change.

## Prompt log

See [prompt_log.md](prompt_log.md).
