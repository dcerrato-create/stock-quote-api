# Prompt Log

**AI tool used:** Claude Code (VS Code extension), model Claude Opus 5.5 (high effort)

## Key prompts

### 1. Initial project spec

> I've attached the complete HW4 instructions as HW4_instructions.pdf in this folder. Read it fully first and make sure everything you build meets its requirements. Add HW4_instructions.pdf to .gitignore so it isn't committed.
>
> Build a simple, focused HW4 project with no extra features or styling. My GitHub username is dcerrato-create.
>
> Backend (this folder, stock-quote-api):
> - Flask app app.py with flask-cors enabled
> - One endpoint: POST /quote, body {"ticker": "AAPL"}
> - Calls the Finnhub quote API using the key from env var FINNHUB_API_KEY (never hardcoded)
> - Returns JSON {ticker, price, change_percent}
> - Returns a 400 JSON error for an empty ticker and a 404 JSON error for an invalid ticker (Finnhub returns price 0)
> - Use python-dotenv to load .env locally, and run locally on port 5001 (port 5000 conflicts with AirPlay on Mac)
> - requirements.txt (flask, flask-cors, requests, gunicorn, python-dotenv)
> - .gitignore including .env, HW4_instructions.pdf, and Python cache files
> - Create a .env.example showing FINNHUB_API_KEY=your_key_here, then tell me to create .env and paste my key myself. Don't ask me for the key.
> - Render start command: gunicorn app:app
> - Write a README.md covering: (1) endpoints, parameters and responses, (2) how the frontend calls the backend and uses the response, (3) local setup, including the FINNHUB_API_KEY env var, (4) how secrets are handled
> - Create a prompt_log.md listing the AI tool used (Claude Code) and the key prompts I give you in this session
>
> Create a new public GitHub repo for the backend: use the GitHub CLI (gh) ... run git init, make the first commit, then create and push with `gh repo create dcerrato-create/stock-quote-api --public --source=. --push`. Before pushing, confirm that .env is NOT being committed.
>
> Frontend (a separate repo: my existing portfolio at github.com/dcerrato-create/Personal-Website-Portfolio):
> - Create a new folder stock-lookup in it with one index.html: a text input, a button, and a result area.
> - Use fetch() with a BACKEND_URL constant at the top of the script (localhost:5001 for now).
> - Show friendly messages for errors and for the backend being down, plus a "waking up server…" note while loading.
> - Add a link to stock-lookup/ in my portfolio's Projects section.
> - Don't push the portfolio changes until I say so. BACKEND_URL must be switched to the Render URL first.
>
> After creating each file, explain briefly what it does. Then give me the exact commands to test the backend locally with curl.

**What it shaped:** the whole architecture. A single `POST /quote` endpoint, the key kept server-side in an env var, explicit 400/404 JSON errors, port 5001, a separate frontend on GitHub Pages that calls the Render backend through CORS, and the security check before pushing.

### 2. Syncing the portfolio before adding the frontend

> cant you do this? Previous conversations with claude code for previous assignments could edit my github, I dont want to mess up

**What it shaped:** My local portfolio copy was 29 commits behind GitHub. Claude checked that nothing local would be lost, set my uncommitted edits aside with `git stash`, pulled, and only then added the Stock Lookup card to the Projects section.

### 3. How we worked from then on

> From now on don't ask me to run commands. Run every command yourself: installs, tests, curl, git, and gh. Only stop and ask me when something truly needs me: a browser login, pasting my key into .env, or a click in a website dashboard. ... If you havent found my finnhub key yet here it is: [key removed]

**What it shaped:** Claude wrote the key into `.env` (which is gitignored), ran the local curl tests itself (200 for AAPL, 400 for an empty ticker, 404 for a fake one, plus a CORS check), and walked me through the one-time `gh` browser login.

### 4. Upgrading to a portfolio-worthy version

> Upgrade the stock lookup to be portfolio-worthy while keeping it simple, using Finnhub only.
>
> Backend (stock-quote-api):
> - Keep POST /quote. Have it also call Finnhub's free /stock/profile2 and /stock/metric?metric=all endpoints.
> - Return JSON: ticker, company name, logo URL, price, change, change_percent, open, high, low, previous close, 52-week high/low, P/E and market cap.
> - Keep the existing error handling. If profile or metrics fail, still return the quote.
> - Add a new endpoint GET /search?q=<text> that calls Finnhub's /search endpoint and returns up to 6 matches as JSON: [{symbol, name}]. Only include US common stocks (skip symbols containing a "."). Return an empty list for empty input, and a JSON error if Finnhub fails.
> - Update README.md with both endpoints and their new response fields. Near the top, add: "This project follows the 'fetch data from an API that requires authentication' pattern: ..."
> - Add this prompt to prompt_log.md.
>
> Frontend (stock-lookup/index.html):
> - Title: "David's Stock Lookup"
> - Match my portfolio's look by reading the portfolio's CSS and reusing its fonts, colors and spacing.
> - Autocomplete: as the user types a ticker or company name (e.g. "AP" or "apple"), call /search, waiting about 300ms after they stop typing so it doesn't call on every keystroke. Show a dropdown of "AAPL — Apple Inc." style suggestions. Clicking one, or using the arrow keys plus Enter, fills the input and runs the quote. If there are no matches, show "No matches."
> - A result card with the logo and company name, a large price, the $/% change in green or red, and a small grid of the day stats and key metrics.
> - Quick-pick buttons: AAPL, NVDA, MSFT, TSLA
> - Keep the loading message ("waking up server…") and friendly errors.
> - Don't add charts or anything that needs a database.
>
> Run everything yourself and test locally: autocomplete with "AP" and "apple", a quote, an empty input, a fake ticker, and the backend being down. Don't push the portfolio yet.

**What it shaped:** `/quote` now makes one required Finnhub call (quote) and two optional ones (profile, metrics) that fail softly. The new `/search` endpoint filters to US common stocks. The frontend reuses the portfolio's design tokens (Inter, near-black background, Honduran-blue accent, pill buttons) and adds a debounced, keyboard-accessible autocomplete. Claude tested every case above with curl, and with an automated Chrome run using Playwright, before deploying.

### 5. Berkshire Hathaway didn't work

> From now on dont worry about changes in the README file and prompt log, We wil work on those at the end once everything is pushed into github ... I tried berkshire hathaway and it did not work. DIALOGUE ONLY, how can we make that work

**What it shaped:** Claude explained that the "skip dotted symbols" rule was hiding share classes like BRK.A/BRK.B, and proposed allowing share-class tickers and accepting spellings like BRK-B.

### 6. ETFs and indexes

> WAIT, before changing, etfs and indexes dont work?

**What it shaped:** Before changing anything, Claude checked Finnhub directly. ETFs had prices but were filtered out of search and had no company profile. Indexes (^GSPC) have no data on the free plan. BRK.B gets BRK.A's 52-week range.

> Yes, do all three, quick modifications tho. At the very top make a note of what works and what does not, for example, US equities, ADRs, and ETFs work, indexes do not. AND only if you can, when people search up, create an indicator that lets them know if this is either an ETF or stock. For the indexes, I like your idea, do it that way. Go

**What it shaped:**
- ETFs and ADRs are included in search, with Stock/ETF badges on suggestions and the result card.
- Index lookups get a message pointing to a tracking ETF (SPY/DIA/QQQ/IWM), and typing an index name suggests that ETF.
- Share classes are supported, with the BRK-B spelling accepted.
- A coverage note sits at the top of the page, and SPY was added to the quick picks.

### 7. Edge cases and frontend-backend communication

> The instruction say the following: "Focus on core functionality and clean communication between frontend and backend rather than UI polish." I believe our UI is functional enough, I just really want to make sure on the communication between backend and frontend. Can you make a last test for edgecases and make sure errors and handled adequately. For example, if we need to add a special note for the berkshire example edgecase. DONT worry about pushing yet ... THE SPY shows a stock badge when it clearly is a etf, and the etf search bar suggestions dont work

**What it shaped:**
- Claude found that the page was still talking to the old Render deploy, and that the frontend guessed "Stock" when no type was sent. Both were fixed.
- The backend now sends `notes` that explain hidden numbers.
- Every response is JSON, including 404/405/500. Input is validated, and Finnhub 429 and 401 errors get their own messages.
- The frontend gained a 70 s timeout, ignores stale responses and validates replies.
- About 60 automated checks: backend tests with simulated Finnhub failures, plus Playwright browser tests of odd replies, CORS blocking, timeouts and HTML injection.

### 8. Foreign companies in search

> voo works actually, why wouldnt toyota work?

> yes do 1+2

**What it shaped:** Finnhub's name search maps "toyota" to Tokyo's 7203.T, not the US ADR TM. Claude added:
- a short verified list of well-known foreign companies mapped to their US tickers (toyota → TM, tsmc → TSM, ...), which still works when Finnhub is rate-limited
- a clearer "No matches. Try the ticker instead" message

### 9. Price time, penny stocks, ADR notes

> Yes do that change for cheap stock, and modify the notes for ADR on why the 52 week info doesnt show up, mention that this is exclusive to ADR. Do that change of the time of the price, really good to change that.

**What it shaped:**
- An `as_of` field and an "As of Fri, Sep 25, 4:00 PM ET · change vs. previous close" line replace the misleading "today". OTC stocks show a date only.
- Prices under $1 show up to 4 decimals.
- ADRs are detected from Finnhub's non-USD currency. This also uncovered that ADR market caps were shown in yen or Taiwan dollars as if they were USD.

> two final change, maybe we display the market cap simply change the symbol from dollar to the actual currency and add a separate note for ADR. Then I tested penny stock GGSM and it appears 0.00

> why would that be wrong for those ADR's?

> OK, you are right, do that final change for ADR, everything else looks good, but dont push yet

**What it shaped:** Claude checked 11 ADRs and found that Finnhub's `currency` field is the filing currency: Alibaba, Baidu and PDD are labeled CNY while their market caps are in USD. ADR market caps are therefore hidden, with their own note, separate from the 52-week note. GGSM displayed correctly; the tab had been opened before the fix.

### 10. Final edge-case sweep

> CAN you make any final check for edgecases

**What it shaped:** The sweep ran the backend under gunicorn (as on Render), scanned every response for the API key (found in none), and tested phone layout and double submits. It found and fixed three issues:
- Mutual funds (a Finnhub 403) were reported as "API key rejected".
- Queries with "+" (a Finnhub 422) showed a fake outage.
- Accented names like "nestlé" didn't match the hints.

### 11. Finish and push

> Finish HW4 and push everything. Run every command yourself, only stop when a step truly needs my hands (a website click or login), and then give me one plain-English step at a time with no terminal commands. Re-read HW4_instructions.pdf and make sure everything below meets it. 1. Safety checks before any push ... 2. Push the backend ... 3. Deploy to Render ... 4. Push the frontend ... 5. Final verification ...

**What it shaped:** Safety checks came first: `.env` and the PDF ignored and untracked, the key absent from every tracked file and all history in both repos, CORS verified for the GitHub Pages origin. Then the README was rewritten for the final API, this log was updated, the backend was pushed (Render auto-deploys) and tested live, `BACKEND_URL` was switched to Render, and the portfolio was pushed and verified on GitHub Pages.
