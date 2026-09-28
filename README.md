# Stock Quote API

A Flask backend for David's Stock Lookup, a page on my portfolio that shows live stock data from the Finnhub API. This project follows the 'fetch data from an API that requires authentication' pattern: the backend holds the Finnhub API key as a Render environment variable and proxies requests, so the key is never exposed in frontend code.

Live backend: https://stock-quote-api-t5yy.onrender.com. Live page: https://dcerrato-create.github.io/Personal-Website-Portfolio/stock-lookup/. Frontend repo: https://github.com/dcerrato-create/Personal-Website-Portfolio.

## What the backend does

The backend has two endpoints. POST /quote takes a JSON body with a ticker. It returns that stock's price, daily change, company name and logo, day stats, 52-week range, P/E ratio and market cap, plus short notes explaining any number it had to hide. GET /search takes a q parameter containing part of a ticker or company name, and returns up to six matching US stocks, ADRs and ETFs, each labeled Stock or ETF. Errors also come back as JSON with a readable message: an empty or unknown ticker, an index (the message points you to an ETF that tracks it), or the data provider being unavailable. Opening the base URL in a browser shows a short summary confirming the API is running.

## How the frontend communicates with the backend

As the user types, the page waits for a short pause and then calls /search to show autocomplete suggestions. Picking a suggestion, pressing Get Quote or clicking a quick-pick button calls /quote. The page turns that response into a card showing the price, change, stats and notes. If the backend returns an error, is still waking up or can't be reached, the page shows a friendly message instead.

## How to set up and run the backend

Clone the repo, create a Python virtual environment and install the packages listed in requirements.txt. Copy .env.example to .env and set FINNHUB_API_KEY to your own free Finnhub key. Then run app.py, which starts the server locally on port 5001. On Render, the same app runs with gunicorn, and the key is set as an environment variable in the dashboard.

## How secrets are handled

The Finnhub key exists only on the backend: in a local .env file that git ignores, and as an environment variable on Render. The browser only ever talks to this backend, never to Finnhub directly, so the key never appears in the frontend code or in any response.



