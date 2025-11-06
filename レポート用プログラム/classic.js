(() => {
  const WIN_LINES = [
    [0,1,2],[3,4,5],[6,7,8],
    [0,3,6],[1,4,7],[2,5,8],
    [0,4,8],[2,4,6]
  ];

  let board;      // Array(9) of ' ' | '○' | '×'
  let current;    // '○' | '×'
  let finished;   // boolean

  const boardEl = document.getElementById('board');
  const statusEl = document.getElementById('status');
  const modalEl = document.getElementById('modal');
  const modalMsgEl = document.getElementById('modal-message');
  const btnRematch = document.getElementById('btn-rematch');
  const btnExit = document.getElementById('btn-exit');

  const cellEls = [];

  function initUI() {
    boardEl.innerHTML = '';
    cellEls.length = 0;
    for (let i = 0; i < 9; i++) {
      const cell = document.createElement('div');
      cell.className = 'cell';
      cell.setAttribute('role', 'button');
      cell.setAttribute('aria-label', `マス ${i+1}`);
      cell.addEventListener('click', () => onCell(i));
      cellEls.push(cell);
      boardEl.appendChild(cell);
    }
    btnRematch.addEventListener('click', () => { hideModal(); newGame(); });
    btnExit.addEventListener('click', () => {
      hideModal();
      finished = true;
      updateInteractivity();
      statusEl.textContent = 'ゲームを終了しました。ページ再読み込みで再開できます。';
    });
  }

  function newGame() {
    board = Array(9).fill(' ');
    current = '○';
    finished = false;
    for (const el of cellEls) {
      el.textContent = '';
      el.classList.remove('disabled', 'allowed');
      el.style.pointerEvents = 'auto';
    }
    updateStatus();
  }

  function onCell(idx) {
    if (finished) return;
    if (board[idx] !== ' ') return;
    place(idx, current);
    const win = winner(board, current);
    if (win) { return finish(`${current} の勝ちです！`); }
    if (isDraw(board)) { return finish('引き分けでした。'); }
    current = current === '○' ? '×' : '○';
    updateStatus();
  }

  function place(idx, mark) {
    board[idx] = mark;
    cellEls[idx].textContent = mark;
    cellEls[idx].classList.add('disabled');
    cellEls[idx].style.pointerEvents = 'none';
  }

  function updateInteractivity() {
    for (let i = 0; i < 9; i++) {
      const clickable = !finished && board[i] === ' ';
      cellEls[i].style.pointerEvents = clickable ? 'auto' : 'none';
    }
  }

  function updateStatus() {
    statusEl.textContent = `${current} の番です`;
  }

  function winner(b, mark) {
    return WIN_LINES.some(([a,b1,c]) => b[a] === mark && b[b1] === mark && b[c] === mark);
  }

  function isDraw(b) { return b.every(v => v !== ' '); }

  function finish(message) {
    finished = true;
    updateInteractivity();
    statusEl.textContent = message;
    showModal(`${message} 再戦しますか？`);
  }

  function showModal(message) {
    modalMsgEl.textContent = message;
    modalEl.classList.remove('hidden');
  }
  function hideModal() { modalEl.classList.add('hidden'); }

  // boot
  initUI();
  newGame();
})();

