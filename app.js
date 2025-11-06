// Ultimate Tic-Tac-Toe (3x3 micro boards × 3x3 macro)
// 送先制約: 常に有効（次に打つミクロ盤は直前に置いたセル番号）

(() => {
  const WIN_LINES = [
    [0,1,2],[3,4,5],[6,7,8], // rows
    [0,3,6],[1,4,7],[2,5,8], // cols
    [0,4,8],[2,4,6]          // diagonals
  ];

  // 状態
  let boards;           // Array(9) of Array(9) ' '/ '○' / '×'
  let microWinner;      // Array(9) of null / '○' / '×' / 'draw'
  let current;          // '○' or '×'
  let forcedBoard;      // null or 0..8
  let macroWinner;      // null or { winner: '○'|'×'|'draw', line: [a,b,c]|null }
  let ended;            // true when finished and exited

  // 要素参照
  const macroEl = document.getElementById('macro');
  const statusEl = document.getElementById('status');
  const modalEl = document.getElementById('modal');
  const modalMsgEl = document.getElementById('modal-message');
  const btnRematch = document.getElementById('btn-rematch');
  const btnExit = document.getElementById('btn-exit');

  const microEls = [];       // 9 micro containers
  const cellEls = [];        // 9 arrays of 9 cell divs
  const overlayEls = [];     // 9 overlay labels

  function initUI() {
    macroEl.innerHTML = '';
    microEls.length = 0;
    cellEls.length = 0;
    overlayEls.length = 0;

    for (let m = 0; m < 9; m++) {
      const micro = document.createElement('div');
      micro.className = 'micro';
      micro.setAttribute('data-micro', String(m));

      const cells = document.createElement('div');
      cells.className = 'cells';
      const list = [];
      for (let i = 0; i < 9; i++) {
        const cell = document.createElement('div');
        cell.className = 'cell';
        cell.setAttribute('role', 'button');
        cell.setAttribute('aria-label', `ミクロ${m+1}のマス${i+1}`);
        cell.addEventListener('click', () => onCellClick(m, i));
        list.push(cell);
        cells.appendChild(cell);
      }

      const overlay = document.createElement('div');
      overlay.className = 'overlay';
      overlay.textContent = '';

      micro.appendChild(cells);
      micro.appendChild(overlay);
      macroEl.appendChild(micro);

      microEls.push(micro);
      cellEls.push(list);
      overlayEls.push(overlay);
    }

    btnRematch.addEventListener('click', () => {
      hideModal();
      newGame();
    });
    btnExit.addEventListener('click', () => {
      hideModal();
      // 終了: 盤面を無効化（ブラウザはウィンドウを閉じられない可能性が高い）
      ended = true;
      updateInteractivity();
      statusEl.textContent = 'ゲームを終了しました。ページを再読み込みで再開できます。';
    });
  }

  function newGame() {
    boards = Array.from({ length: 9 }, () => Array(9).fill(' '));
    microWinner = Array(9).fill(null);
    current = '○';
    forcedBoard = null;
    macroWinner = null;
    ended = false;

    // UI reset
    for (let m = 0; m < 9; m++) {
      microEls[m].classList.remove('won', 'allowed');
      overlayEls[m].textContent = '';
      for (let i = 0; i < 9; i++) {
        const el = cellEls[m][i];
        el.textContent = '';
        el.classList.remove('disabled', 'allowed');
      }
    }

    updateStatus();
    highlightAllowed();
    updateInteractivity();
  }

  function onCellClick(microIdx, cellIdx) {
    if (ended || macroWinner) return;
    if (boards[microIdx][cellIdx] !== ' ') return;
    if (microWinner[microIdx]) return;
    if (forcedBoard !== null && microIdx !== forcedBoard) return; // 送先制約

    // 置く
    place(microIdx, cellIdx, current);

    // ミクロ勝敗
    const wline = checkWinner(boards[microIdx], current);
    if (wline) {
      finishMicro(microIdx, current, wline);
    } else if (isDraw(boards[microIdx])) {
      finishMicro(microIdx, 'draw', null);
    }

    // マクロ勝敗
    const macro = checkMacroWinner();
    if (macro) {
      macroWinner = macro;
      finishMacro(macro.winner, macro.line);
      return;
    }

    // 次の送先
    updateForcedBoard(cellIdx);

    // 手番交代
    current = current === '○' ? '×' : '○';
    updateStatus();
    highlightAllowed();
    updateInteractivity();
  }

  function place(microIdx, cellIdx, mark) {
    boards[microIdx][cellIdx] = mark;
    const el = cellEls[microIdx][cellIdx];
    el.textContent = mark;
    el.classList.add('disabled');
  }

  function finishMicro(microIdx, winner, line) {
    microWinner[microIdx] = winner;
    if (winner === '○' || winner === '×') {
      // 大きなマークを表示、セルは隠す
      microEls[microIdx].classList.add('won');
      overlayEls[microIdx].textContent = winner;
    } else {
      // 引き分け: すべて無効化（表示は残す）
      for (const el of cellEls[microIdx]) el.classList.add('disabled');
    }
  }

  function checkWinner(board, mark) {
    for (const [a,b,c] of WIN_LINES) {
      if (board[a] === mark && board[b] === mark && board[c] === mark) return [a,b,c];
    }
    return null;
  }

  function isDraw(board) { return board.every(v => v !== ' '); }

  function checkMacroWinner() {
    for (const [a,b,c] of WIN_LINES) {
      const A = microWinner[a], B = microWinner[b], C = microWinner[c];
      if ((A === '○' || A === '×') && A === B && B === C) {
        return { winner: A, line: [a,b,c] };
      }
    }
    if (microWinner.every(w => w !== null)) return { winner: 'draw', line: null };
    return null;
  }

  function updateForcedBoard(lastCell) {
    const target = lastCell; // 0..8
    const done = microWinner[target] !== null || isDraw(boards[target]);
    forcedBoard = done ? null : target;
  }

  function highlightAllowed() {
    for (let m = 0; m < 9; m++) {
      const free = microWinner[m] === null && !isDraw(boards[m]);
      const allowed = free && (forcedBoard === null || forcedBoard === m);
      microEls[m].classList.toggle('allowed', allowed);
      // optional: cell background hint
      for (let i = 0; i < 9; i++) {
        const el = cellEls[m][i];
        const cellFree = boards[m][i] === ' ';
        el.classList.toggle('allowed', allowed && cellFree);
      }
    }
  }

  function updateInteractivity() {
    for (let m = 0; m < 9; m++) {
      for (let i = 0; i < 9; i++) {
        const el = cellEls[m][i];
        const clickable = !ended && !macroWinner && boards[m][i] === ' ' && microWinner[m] === null && (forcedBoard === null || forcedBoard === m);
        el.style.pointerEvents = clickable ? 'auto' : 'none';
      }
    }
  }

  function updateStatus() {
    if (macroWinner) return;
    const tail = forcedBoard === null ? '— 任意の未確定ミクロ盤に着手可' : `— 指定ミクロ盤: ${forcedBoard + 1}`;
    statusEl.textContent = `${current} の番 ${tail}`;
  }

  function finishMacro(winner, line) {
    // すべて操作不可
    updateInteractivity();
    // ステータス更新
    if (winner === 'draw') {
      statusEl.textContent = 'マクロは引き分けです。';
      showModal('引き分けでした。再戦しますか？');
    } else {
      statusEl.textContent = `${winner} がマクロで勝ちました！`;
      showModal(`${winner} の勝ちです！再戦しますか？`);
    }
  }

  function showModal(message) {
    modalMsgEl.textContent = message;
    modalEl.classList.remove('hidden');
  }
  function hideModal() { modalEl.classList.add('hidden'); }

  // 起動
  initUI();
  newGame();
})();

