from fastapi.testclient import TestClient

import tictactoe
from main import app

client = TestClient(app)


def test_page_renders():
    res = client.get("/")
    assert res.status_code == 200
    assert "<h1>Tic-Tac-Toe AI</h1>" in res.text
    assert res.text.count('class="cell"') == 9
    assert '<meta name="description"' in res.text
    assert 'rel="canonical"' not in res.text  # only emitted when SITE_URL is set
    assert client.get("/static/style.css").status_code == 200
    assert client.get("/static/app.js").status_code == 200
    assert client.get("/static/favicon.svg").status_code == 200
    assert client.get("/robots.txt").text.startswith("User-agent: *")


def test_ai_opens_when_it_is_x():
    res = client.post("/api/move", json={"board": [""] * 9, "ai": "X"})
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "playing"
    assert data["board"][data["move"]] == "X"


def test_ai_takes_an_immediate_win_over_blocking():
    board = ["O", "O", "", "X", "X", "", "", "", "X"]
    data = client.post("/api/move", json={"board": board, "ai": "O"}).json()
    assert data["move"] == 2
    assert data["status"] == "won" and data["winner"] == "O"
    assert data["line"] == [0, 1, 2]


def test_ai_blocks_a_threat():
    board = ["X", "X", "", "", "O", "", "", "", ""]
    data = client.post("/api/move", json={"board": board, "ai": "O"}).json()
    assert data["move"] == 2


def test_finished_board_is_reported_without_a_move():
    board = ["X", "X", "X", "O", "O", "", "", "", ""]
    data = client.post("/api/move", json={"board": board, "ai": "O"}).json()
    assert data["move"] is None
    assert data["status"] == "won" and data["winner"] == "X"


def test_rejects_wrong_turn_and_bad_boards():
    assert client.post("/api/move", json={"board": [""] * 9, "ai": "O"}).status_code == 400
    assert client.post("/api/move", json={"board": ["X"] * 5 + [""] * 4, "ai": "O"}).status_code == 400
    assert client.post("/api/move", json={"board": ["Z"] + [""] * 8, "ai": "O"}).status_code == 422
    assert client.post("/api/move", json={"board": [""] * 8, "ai": "O"}).status_code == 422


def _human_can_win(board: str, to_move: str, ai: str) -> bool:
    """Explore every human reply and every optimal AI reply."""
    state, winner, _ = tictactoe.status(board)
    if state != "playing":
        return winner is not None and winner != ai
    if to_move == ai:
        moves = tictactoe.best_moves(board, ai)
    else:
        moves = [i for i, c in enumerate(board) if c == tictactoe.EMPTY]
    return any(
        _human_can_win(tictactoe.play(board, i, to_move), tictactoe.other(to_move), ai)
        for i in moves
    )


def test_ai_never_loses_as_either_side():
    empty = tictactoe.EMPTY * 9
    assert not _human_can_win(empty, "X", ai="O")
    assert not _human_can_win(empty, "X", ai="X")
