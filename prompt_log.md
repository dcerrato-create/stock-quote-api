# Prompt Log

**AI tool used:** Claude Code (VS Code extension), model Claude Opus 5.5

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
