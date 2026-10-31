from functools import lru_cache
from random import choice

EMPTY = " "
LINES = (
    (0, 1, 2), (3, 4, 5), (6, 7, 8),  
    (0, 3, 6), (1, 4, 7), (2, 5, 8),  
    (0, 4, 8), (2, 4, 6),          
)


def other(player: str) -> str:
    return "O" if player == "X" else "X"


def winning_line(board: str) -> tuple[int, int, int] | None:
    for line in LINES:
        a, b, c = line
        if board[a] != EMPTY and board[a] == board[b] == board[c]:
            return line
    return None


def status(board: str) -> tuple[str, str | None, tuple[int, int, int] | None]:
    """Return (status, winner, line) where status is 'won', 'draw' or 'playing'."""
    line = winning_line(board)
    if line:
        return "won", board[line[0]], line
    if EMPTY not in board:
        return "draw", None, None
    return "playing", None, None


def play(board: str, index: int, player: str) -> str:
    return board[:index] + player + board[index + 1:]


@lru_cache(maxsize=None)
def _negamax(board: str, player: str) -> int:
    """Best score `player` (to move) can force. Positive = win; magnitude prefers quick wins and slow losses."""
    if winning_line(board):
        return -(1 + board.count(EMPTY))  # the opponent just completed a line
    if EMPTY not in board:
        return 0
    return max(
        -_negamax(play(board, i, player), other(player))
        for i, cell in enumerate(board)
        if cell == EMPTY
    )


def best_moves(board: str, player: str) -> list[int]:
    """All optimal moves for `player` on `board`."""
    scored = {
        i: -_negamax(play(board, i, player), other(player))
        for i, cell in enumerate(board)
        if cell == EMPTY
    }
    best = max(scored.values())
    return [i for i, score in scored.items() if score == best]


def best_move(board: str, player: str) -> int:
    return choice(best_moves(board, player))
