# Prompt Log

**AI tool used:** Claude Code (VS Code extension), model Claude Opus 5.5 (high effort)

This log lists every prompt that led to code or repository changes, word for word, in the order I gave them. Purely conversational questions are left out. My Finnhub API key, which I pasted in one prompt, is replaced with [key removed].

---

## Initial project spec

> I've attached the complete HW4 instructions as HW4_instructions.pdf in this folder. Read it fully first and make sure everything you build meets its requirements. Add HW4_instructions.pdf to .gitignore so it isn't committed.
>
> Build a simple, focused HW4 project with no extra features or styling. My GitHub username is dcerrato-create.
>
> Backend (this folder, stock-quote-api):
>
> Flask app app.py with flask-cors enabled
>
> One endpoint: POST /quote, body {"ticker": "AAPL"}
>
> Calls the Finnhub quote API using the key from env var FINNHUB_API_KEY (never hardcoded)
>
> Returns JSON {ticker, price, change_percent}
>
> Returns a 400 JSON error for an empty ticker and a 404 JSON error for an invalid ticker (Finnhub returns price 0)
>
> Use python-dotenv to load .env locally, and run locally on port 5001 (port 5000 conflicts with AirPlay on Mac)
>
> requirements.txt (flask, flask-cors, requests, gunicorn, python-dotenv)
>
> .gitignore including .env, HW4_instructions.pdf, and Python cache files
>
> Create a .env.example showing FINNHUB_API_KEY=your_key_here, then tell me to create .env and paste my key myself. Don't ask me for the key.
>
> Render start command: gunicorn app:app
>
> Write a README.md covering: (1) endpoints, parameters and responses, (2) how the frontend calls the backend and uses the response, (3) local setup, including the FINNHUB_API_KEY env var, (4) how secrets are handled
>
> Create a prompt_log.md listing the AI tool used (Claude Code) and the key prompts I give you in this session
>
> Create a new public GitHub repo for the backend:
>
> Use the GitHub CLI (gh). If it isn't installed, install it with Homebrew. If I'm not logged in, run gh auth login and walk me through the browser login step by step.
>
> Run git init, make the first commit, then create and push with: gh repo create dcerrato-create/stock-quote-api --public --source=. --push
>
> Before pushing, confirm that .env is NOT being committed.
>
> Frontend (a separate repo: my existing portfolio at github.com/dcerrato-create/Personal-Website-Portfolio):
>
> Ask me for the local path of that repo on my Mac. If I don't have it locally, clone it into the folder next to this one.
>
> Create a new folder stock-lookup in it with one index.html: a text input, a button, and a result area.
>
> Use fetch() with a BACKEND_URL constant at the top of the script (localhost:5001 for now).
>
> Show friendly messages for errors and for the backend being down, plus a "waking up server…" note while loading.
>
> Add a link to stock-lookup/ in my portfolio's Projects section.
>
> Don't push the portfolio changes until I say so. BACKEND_URL must be switched to the Render URL first.
>
> After creating each file, explain briefly what it does. Then give me the exact commands to test the backend locally with curl.

**What it shaped:** Claude built the Flask backend with one `POST /quote` endpoint that keeps the Finnhub key in an environment variable and returns JSON errors. It also wrote the supporting files, the README and this log. It committed only the intended files after confirming `.env` was ignored, installed the official `gh` release because Homebrew wasn't available, and created the first `stock-lookup` page in my portfolio.

---

## Syncing the portfolio safely before adding the Projects link

> cant you do this? Previous conversations with claude code for previoous assignments could edit my githib, I dont want to mess up

**What it shaped:** Claude synced my outdated local portfolio with GitHub by setting my uncommitted edits aside in a stash and pulling, so nothing was lost. It then added a Stock Lookup card to the Projects section that matches my other project cards.

---

## Letting Claude run every command

> I made a mistake in my first prompt, from now on don't ask me to run commands. Run every command yourself: installs, tests, curl, git, and gh. Only stop and ask me when something truly needs me: a browser login, pasting my key into .env, or a click in a website dashboard. When that happens, give me one simple step at a time in plain English, with no terminal commands. If you havent find my finhub key yet here it is: [key removed] (and sorry for the initial confusion)

**What it shaped:** Claude took over all commands. It saved the key to the gitignored `.env`, tested the backend with curl and handled the GitHub login. It then created and pushed the public backend repo and walked me through deploying on Render's free tier.

---

## Upgrading to a portfolio-worthy version

> Yeah, dont worry, I didnt say it was bad, here is where we add some cool stuff worthy of going in my portfolio:
>
> Upgrade the stock lookup to be portfolio-worthy while keeping it simple, using Finnhub only.
>
> Backend (stock-quote-api):
>
> Keep POST /quote. Have it also call Finnhub's free /stock/profile2 and /stock/metric?metric=all endpoints.
>
> Return JSON: ticker, company name, logo URL, price, change, change_percent, open, high, low, previous close, 52-week high/low, P/E and market cap.
>
> Keep the existing error handling. If profile or metrics fail, still return the quote.
>
> Add a new endpoint GET /search?q=&lt;text&gt; that calls Finnhub's /search endpoint and returns up to 6 matches as JSON: [{symbol, name}]. Only include US common stocks (skip symbols containing a "."). Return an empty list for empty input, and a JSON error if Finnhub fails.
>
> Update README.md with both endpoints and their new response fields. Near the top, add: "This project follows the 'fetch data from an API that requires authentication' pattern: the backend holds the Finnhub API key as a Render environment variable and proxies requests, so the key is never exposed in frontend code."
>
> Add this prompt to prompt_log.md.
>
> Frontend (stock-lookup/index.html):
>
> Title: "David's Stock Lookup"
>
> Match my portfolio's look by reading the portfolio's CSS and reusing its fonts, colors and spacing.
>
> Autocomplete: as the user types a ticker or company name (e.g. "AP" or "apple"), call /search, waiting about 300ms after they stop typing so it doesn't call on every keystroke. Show a dropdown of "AAPL — Apple Inc." style suggestions. Clicking one, or using the arrow keys plus Enter, fills the input and runs the quote. If there are no matches, show "No matches."
>
> A result card with the logo and company name, a large price, the $/% change in green or red, and a small grid of the day stats and key metrics.
>
> Quick-pick buttons: AAPL, NVDA, MSFT, TSLA
>
> Keep the loading message ("waking up server…") and friendly errors.
>
> Don't add charts or anything that needs a database.
>
> Run everything yourself and test locally: autocomplete with "AP" and "apple", a quote, an empty input, a fake ticker, and the backend being down. Don't push the portfolio yet.

**What it shaped:** The backend gained company info, key metrics and a new `/search` endpoint, and a failure in the extra data never breaks a quote. The page was restyled to match my portfolio, with a debounced autocomplete, a result card and quick-pick buttons. Claude tested everything with curl and automated Chrome tests before deploying.

---

## ETFs, indexes, Berkshire Hathaway and a coverage note

> Yes, do all three, quick modifications tho. At the very top make a note of what works and what does not, for example, US equities, ADRs, and ETFs work, indexes do not. AND only if you can, when people search up, create an indicator that lets them know if this is either an ETF or stock For the indexes, I lioke your idea, do it that way. Go

**What it shaped:** Search now includes ETFs and ADRs, with Stock/ETF badges. Share classes like BRK.B work in any spelling, and index lookups point to an ETF that tracks the index. A note at the top of the page explains what works and what doesn't.

---

## Edge cases and clean frontend-backend communication

> The instruction say the following:  "Focus on core functionality and clean communication between frontend and backend rather than UI polish. " I believ our UI is functional enough, I just really want to make sure on the communication between backend and frontend. Can you make a last test for edgecases and make sure errors and handled adequately. For example, if we need to add a special not for the berkshire example edgecase. DONT worry about pushing yet, dont get ahead of yourself, i want to make sure THIS WORKS FIRST.  THE SPY shows a tock badge when it c;lear;ly is a eft, and the etf search bar suggestions dont work

**What it shaped:** Claude found that Render was still running the old backend, and fixed a bug where the page guessed "Stock" when the type was unknown. Every backend response is now readable JSON, with input checks, rate-limit messages, timeouts and notes that explain hidden numbers. About 60 automated backend and browser tests verified it.

---

## Finding foreign companies by name

> yes do 1+2

**What it shaped:** Typing a well-known foreign company name like "toyota" now suggests its US ticker, TM. Searches with no results suggest trying the ticker instead.

---

## Price time, penny stocks and ADR notes

> Yes do that change for cheap stock, and modify the notes for ADR on why the 52 week info doesnt show up, mentiuon that this is exclusive to ADR. Do that change of the time of the price, really good to change that.

**What it shaped:** The card now shows when the price is from, where it used to say "today", and penny stocks show up to four decimals. ADRs hide figures that Finnhub reports in a foreign currency, with a note saying this only affects ADRs.

---

## Market cap currency and GGSM

> two final change, maybe we display the market cna simply change the symbol from dollar to the actually current and add a sepearte not for ADR. Then I tested penny stock GGSM and it appears 0.00

**What it shaped:** Showing ADR market caps in their home currency revealed that Finnhub mislabels some of them: Alibaba's is in US dollars but labeled yuan. The GGSM check found it displayed correctly, and led to shorter market caps like $513.75K and date-only times for over-the-counter stocks.

---

## Hiding ADR market caps

> OK, you are right, do that final change for ADR, everything else looks good, but dont push yet

**What it shaped:** ADR market caps are now hidden with their own note, separate from the 52-week note.

---

## Final edge-case sweep

> CAN you make any final check for edgecases

**What it shaped:** Testing in production mode found and fixed three issues: mutual funds were reported as an API key error, searches containing "+" showed a fake outage, and accented names like "nestlé" didn't match. The API key appeared in none of the responses.

---

## Finish and push

> Alright, the time has come, go. Just to remind you:
>
> Finish HW4 and push everything. Run every command yourself, only stop when a step truly needs my hands (a website click or login), and then give me one plain-English step at a time with no terminal commands. Re-read HW4_instructions.pdf and make sure everything below meets it.
>
> 1. Safety checks before any push
>
> Confirm .env and HW4_instructions.pdf are in .gitignore and not tracked by git.
>
> Search every tracked file in both repos for my Finnhub key. If it appears anywhere, stop and tell me.
>
> Confirm CORS allows https://dcerrato-create.github.io.
>
> 2. Push the backend (stock-quote-api)
>
> Make sure README.md has: the endpoints (POST /quote, GET /search) with their parameters and responses, how the frontend calls each one and uses the response, local setup including FINNHUB_API_KEY, and how secrets are handled. Keep the line saying this follows the "fetch data from an API that requires authentication" pattern. Mention that autocomplete, the quick-pick buttons and the search each call the backend.
>
> Make sure prompt_log.md lists Claude Code (Opus 5.5, high effort) and every key prompt from this session, including this one.
>
> Commit and push to github.com/dcerrato-create/stock-quote-api.
>
> 3. Deploy to Render
>
> Walk me through Render's website one click at a time: create a Web Service from the stock-quote-api repo, use the free tier, build command pip install -r requirements.txt, start command gunicorn app:app, and add FINNHUB_API_KEY as an environment variable. When it's live, ask me for the Render URL.
>
> Test the live URL yourself: /quote with AAPL, /search with "apple", an empty ticker, and a fake ticker. Fix and redeploy if anything fails.
>
> Add the live Render URL to the README and push again.
>
> 4. Push the frontend (Personal-Website-Portfolio)
>
> Change BACKEND_URL in stock-lookup/index.html from localhost to the Render URL.
>
> Confirm the Projects section links to stock-lookup/.
>
> Commit and push.
>
> 5. Final verification
>
> Wait for GitHub Pages to update, then confirm https://dcerrato-create.github.io/Personal-Website-Portfolio/stock-lookup/ loads and points at the Render URL.
>
> Give me a final summary with: the backend repo URL, frontend repo URL, live frontend URL, Render URL, and a confirmation that no secrets are on GitHub.

**What it shaped:** Claude ran the safety checks and updated the README and this log. It pushed the backend and confirmed Render redeployed, then switched the page to the Render URL and pushed the portfolio. Finally it verified the live page works and that no secrets are on GitHub.
