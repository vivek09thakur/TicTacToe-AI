// Game client. The server is stateless: every request carries the whole board.
(() => {
  const moveUrl = document.currentScript.dataset.moveUrl;
  const cells = Array.from(document.querySelectorAll('#board .cell'));
  const boardEl = document.getElementById('board');
  const statusEl = document.getElementById('status');
  const sideInputs = document.querySelectorAll('input[name="side"]');
  const newGameBtn = document.getElementById('new-game');

  const MIN_THINK_MS = 300; // lets the player see their own mark land before the reply
  const TIMEOUT_MS = 8000;

  let board = Array(9).fill('');
  let ai = 'O';
  let locked = false; // AI's turn or game over
  let gameId = 0;

  const you = () => (ai === 'X' ? 'O' : 'X');

  function setStatus(text, tone = '') {
    statusEl.textContent = text;
    statusEl.dataset.tone = tone;
  }

  function render(line = []) {
    cells.forEach((cell, i) => {
      const mark = board[i];
      const row = Math.floor(i / 3) + 1;
      const col = (i % 3) + 1;
      cell.textContent = mark;
      cell.setAttribute('aria-label', `Row ${row}, column ${col}, ${mark || 'empty'}`);
      cell.setAttribute('aria-disabled', String(locked || mark !== ''));
      if (mark) cell.dataset.mark = mark; else delete cell.dataset.mark;
      if (line.includes(i)) cell.dataset.win = ''; else delete cell.dataset.win;
    });
  }

  function finish(result) {
    locked = true;
    render(result.line || []);
    if (result.status === 'draw') setStatus("It's a draw");
    else setStatus(result.winner === ai ? 'AI wins' : 'You win');
  }

  async function requestAiMove(humanIndex) {
    const id = gameId;
    locked = true;
    boardEl.setAttribute('aria-busy', 'true');
    render();
    setStatus('AI is thinking…', 'busy');

    const started = performance.now();
    try {
      const res = await fetch(moveUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ board, ai }),
        signal: AbortSignal.timeout(TIMEOUT_MS),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const result = await res.json();
      await new Promise((r) => setTimeout(r, Math.max(0, MIN_THINK_MS - (performance.now() - started))));
      if (id !== gameId) return;

      board = result.board;
      if (result.status === 'playing') {
        locked = false;
        render();
        setStatus('Your turn');
      } else {
        finish(result);
      }
    } catch {
      if (id !== gameId) return;
      if (humanIndex !== undefined) {
        board[humanIndex] = ''; // undo so the player can retry the move
        locked = false;
      }
      render();
      setStatus("Couldn't reach the AI. Try again.", 'error');
    } finally {
      if (id === gameId) boardEl.removeAttribute('aria-busy');
    }
  }

  function newGame() {
    gameId += 1;
    board = Array(9).fill('');
    locked = false;
    boardEl.removeAttribute('aria-busy');
    render();
    if (ai === 'X') requestAiMove();
    else setStatus('Your turn');
  }

  cells.forEach((cell, i) => {
    cell.addEventListener('click', () => {
      if (locked || board[i]) return;
      board[i] = you();
      requestAiMove(i);
    });
  });

  sideInputs.forEach((input) => {
    input.addEventListener('change', () => {
      ai = input.value === 'X' ? 'O' : 'X';
      newGame();
    });
  });

  newGameBtn.addEventListener('click', newGame);

  newGame();
})();
