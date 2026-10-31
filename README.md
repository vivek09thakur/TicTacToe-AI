## TIC-TAC-TOE GAME PLAYING AI

An unbeatable Tic-Tac-Toe AI with a FastAPI backend and a plain HTML/CSS/JS frontend. The agent uses a memoised minimax search and will always win or draw.

The server is stateless — the browser sends the whole board with every move — so the app deploys as a single Vercel function.

### Run locally

```bash
python -m venv .venv
.venv\Scripts\activate        # macOS/Linux: source .venv/bin/activate
pip install -r requirements-dev.txt
uvicorn main:app --reload
```

Open http://127.0.0.1:8000. Run the tests (including an exhaustive proof that the AI never loses) with `pytest`.

### Deploy to Vercel

Vercel detects the FastAPI app in `main.py` from `requirements.txt` — no `vercel.json` needed.

- **Git:** push the repo to GitHub and import it at https://vercel.com/new.
- **CLI:** `npm i -g vercel` then `vercel deploy` (or `vercel dev` to run the function locally).

Optionally set a `SITE_URL` environment variable (e.g. `https://your-app.vercel.app`) in the Vercel project so the page emits canonical and Open Graph URL tags.

### API

`POST /api/move` with `{"board": ["X", "", "O", "", "", "", "", "", ""], "ai": "O"}` returns the board after the AI's reply plus `move`, `status` (`playing` · `won` · `draw`), `winner` and the winning `line`.

### DEMO GAMEPLAY

<video width="600" height="400" controls>
  <source src="demo game/demo_game.mp4" type="video/mp4">
</video>

### https://www.youtube.com/watch?v=v8nAjVT5diA