import os
from pathlib import Path
from typing import Literal

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import PlainTextResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field

import tictactoe

ROOT = Path(__file__).parent
DESCRIPTION = (
    "Play tic-tac-toe in your browser against an unbeatable AI that uses minimax search. "
    "Choose X or O — the best you can do is a draw."
)

SITE_URL = os.environ.get("SITE_URL", "").rstrip("/")

app = FastAPI(title="Tic-Tac-Toe AI", docs_url=None, redoc_url=None)
app.mount("/static", StaticFiles(directory=ROOT / "static"), name="static")
templates = Jinja2Templates(directory=ROOT / "templates")

Mark = Literal["X", "O"]
Cell = Literal["X", "O", ""]


class MoveRequest(BaseModel):
    board: list[Cell] = Field(min_length=9, max_length=9)
    ai: Mark


class MoveResponse(BaseModel):
    board: list[Cell]
    move: int | None
    status: Literal["playing", "won", "draw"]
    winner: Mark | None
    line: list[int] | None


@app.get("/", include_in_schema=False)
def index(request: Request):
    return templates.TemplateResponse(
        request, "index.html", {"description": DESCRIPTION, "site_url": SITE_URL}
    )


@app.get("/robots.txt", include_in_schema=False)
def robots():
    return PlainTextResponse("User-agent: *\nAllow: /\n")


@app.post("/api/move", response_model=MoveResponse)
def move(req: MoveRequest):
    board = "".join(cell or tictactoe.EMPTY for cell in req.board)
    lead = board.count("X") - board.count("O")
    if lead not in (0, 1):
        raise HTTPException(400, "Board has an impossible number of marks.")

    state, winner, line = tictactoe.status(board)
    played = None

    if state == "playing":
        if ("X" if lead == 0 else "O") != req.ai:
            raise HTTPException(400, "It is not the AI's turn.")
        played = tictactoe.best_move(board, req.ai)
        board = tictactoe.play(board, played, req.ai)
        state, winner, line = tictactoe.status(board)

    return MoveResponse(
        board=[cell.strip() for cell in board],
        move=played,
        status=state,
        winner=winner,
        line=list(line) if line else None,
    )