import tkinter as tk


WIN_LINES = [
    (0, 1, 2), (3, 4, 5), (6, 7, 8),  # rows
    (0, 3, 6), (1, 4, 7), (2, 5, 8),  # cols
    (0, 4, 8), (2, 4, 6)              # diagonals
]


class UltimateTicTacToeGUI:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("アルティメット ○×ゲーム (3×3 の中に 3×3)")

        # 状態
        self.boards = [[' '] * 9 for _ in range(9)]  # 9つのミクロ盤
        self.micro_winner = [None] * 9               # None / '○' / '×' / 'draw'
        self.current = '○'                           # 手番
        self.forced_board = None                      # 制約ルールで次に打つミクロ盤 (0..8 or None)
        self.macro_winner_line = None
        self.constraint = tk.BooleanVar(value=True)   # 送先制約（次の盤指定）

        # スコア（マクロ結果）
        self.scores = {'○': 0, '×': 0, 'draw': 0}

        # UI
        self._build_ui()
        self._update_status()
        self._highlight_allowed()

    def _build_ui(self):
        ctrl = tk.Frame(self.root)
        ctrl.pack(padx=10, pady=(10, 4), fill='x')
        tk.Button(ctrl, text="スコアリセット", command=self.reset_scores).pack(side='left', padx=8)

        score = tk.Frame(self.root)
        score.pack(padx=10, pady=(0, 6), fill='x')
        self.score_o = tk.Label(score, text="○: 0")
        self.score_x = tk.Label(score, text="×: 0")
        self.score_d = tk.Label(score, text="引き分け: 0")
        self.score_o.pack(side='left', padx=(0, 12))
        self.score_x.pack(side='left', padx=(0, 12))
        self.score_d.pack(side='left')

        self.macro_frame = tk.Frame(self.root)
        self.macro_frame.pack(padx=10, pady=6)

        # 9つのミクロ盤フレーム + 各9ボタン
        self.micro_frames = []
        self.micro_buttons = []  # list[list[Button]]
        self._default_frame_bg = self.root.cget('bg')
        for r in range(3):
            for c in range(3):
                m_idx = r * 3 + c
                f = tk.LabelFrame(self.macro_frame, text=f"{m_idx+1}")
                f.grid(row=r, column=c, padx=6, pady=6, sticky='nsew')
                self.micro_frames.append(f)
                btns = []
                for rr in range(3):
                    for cc in range(3):
                        i = rr * 3 + cc
                        b = tk.Button(f, text=' ', width=3, height=1,
                                      font=("Meiryo UI", 16),
                                      command=lambda mi=m_idx, ci=i: self.on_click(mi, ci))
                        b.grid(row=rr, column=cc, padx=2, pady=2, sticky='nsew')
                        btns.append(b)
                self.micro_buttons.append(btns)

        # ミクロ勝利時に大きな○/×を重ねるためのオーバーレイ
        self.micro_overlays = [None] * 9

        status = tk.Frame(self.root)
        status.pack(padx=10, pady=(0, 10), fill='x')
        self.status_label = tk.Label(status, text="", anchor='w')
        self.status_label.pack(fill='x')

    def _on_toggle_constraint(self):
        # 送先制約の切替時は許可ハイライトだけ更新
        self._highlight_allowed()
        self._update_status()

    def on_click(self, micro_idx: int, cell_idx: int):
        if self.macro_winner_line is not None:
            return
        if self.boards[micro_idx][cell_idx] != ' ':
            return

        # 制約チェック
        if self.constraint.get() and self.forced_board is not None and micro_idx != self.forced_board:
            return
        if self.micro_winner[micro_idx] is not None:
            return

        # 打つ
        self._place(micro_idx, cell_idx, self.current)

        # ミクロ勝敗
        wline = self._check_winner(self.boards[micro_idx], self.current)
        if wline:
            self._finish_micro(micro_idx, self.current, wline)
        elif self._is_draw(self.boards[micro_idx]):
            self._finish_micro(micro_idx, 'draw', None)

        # マクロ勝敗
        macro = self._check_macro_winner()
        if macro:
            winner, line = macro
            self._finish_macro(winner, line)
            return

        # 次の制約計算
        self._update_forced_board(last_cell=cell_idx)

        # 手番交代
        self.current = '×' if self.current == '○' else '○'
        self._update_status()
        self._highlight_allowed()

    def _place(self, micro_idx: int, cell_idx: int, mark: str):
        self.boards[micro_idx][cell_idx] = mark
        self.micro_buttons[micro_idx][cell_idx].config(text=mark, state='disabled')

    def _finish_micro(self, micro_idx: int, winner, line):
        self.micro_winner[micro_idx] = winner
        # 盤面を確定表示
        if winner in ('○', '×'):
            # ボタンを隠し、大きなマークを中央に表示
            for b in self.micro_buttons[micro_idx]:
                b.grid_remove()
            if self.micro_overlays[micro_idx] is None:
                lbl = tk.Label(self.micro_frames[micro_idx], text=winner,
                               font=("Meiryo UI", 42, "bold"))
                lbl.place(relx=0.5, rely=0.5, anchor="center")
                self.micro_overlays[micro_idx] = lbl
            else:
                self.micro_overlays[micro_idx].config(text=winner)
        else:  # draw
            for b in self.micro_buttons[micro_idx]:
                b.config(state='disabled')

    def _check_winner(self, board, mark):
        for a, b, c in WIN_LINES:
            if board[a] == board[b] == board[c] == mark:
                return (a, b, c)
        return None

    def _is_draw(self, board):
        return all(v != ' ' for v in board)

    def _check_macro_winner(self):
        # micro_winner でマクロの勝敗
        for a, b, c in WIN_LINES:
            ma, mb, mc = self.micro_winner[a], self.micro_winner[b], self.micro_winner[c]
            if ma in ('○', '×') and ma == mb == mc:
                return (ma, (a, b, c))
        # 全ミクロ確定で引き分け
        if all(w is not None for w in self.micro_winner):
            return ('draw', None)
        return None

    def _update_forced_board(self, last_cell: int):
        if not self.constraint.get():
            self.forced_board = None
            return
        target = last_cell  # 0..8
        # 送先が既に確定/満杯なら自由
        if self.micro_winner[target] is not None or self._is_draw(self.boards[target]):
            self.forced_board = None
        else:
            self.forced_board = target

    def _highlight_allowed(self):
        # 許可されているミクロ盤を枠色で示す
        for idx, f in enumerate(self.micro_frames):
            color = self._default_frame_bg
            if self.micro_winner[idx] is None and not self._is_draw(self.boards[idx]):
                if not self.constraint.get() or self.forced_board is None or self.forced_board == idx:
                    color = "#fff4cc"  # 許可
            f.config(bg=color)
            for b in self.micro_buttons[idx]:
                # フレーム色に合わせてボタン背景も薄く
                if str(b.cget('state')) == 'normal' and color != self._default_frame_bg:
                    b.config(bg="#fffaf0")
                elif str(b.cget('state')) == 'normal':
                    b.config(bg=self.root.cget('bg'))

    def _finish_macro(self, winner, line):
        self.macro_winner_line = line
        # 許可ハイライト解除 + 全無効化
        for f in self.micro_frames:
            f.config(bg=self._default_frame_bg)
        for btns in self.micro_buttons:
            for b in btns:
                b.config(state='disabled')

        if winner == 'draw':
            self.status_label.config(text="マクロは引き分けです。結果ダイアログで再戦を選べます。")
        else:
            self.status_label.config(text=f"{winner} がマクロで勝ちました！結果ダイアログで再戦を選べます。")

        # スコア更新
        self.scores[winner] += 1
        self._update_scores()

        # 結果ダイアログ
        self._show_result_dialog(winner)

    def _update_scores(self):
        self.score_o.config(text=f"○: {self.scores['○']}")
        self.score_x.config(text=f"×: {self.scores['×']}")
        self.score_d.config(text=f"引き分け: {self.scores['draw']}")

    def reset_scores(self):
        self.scores = {'○': 0, '×': 0, 'draw': 0}
        self._update_scores()

    def _update_status(self):
        if self.macro_winner_line is None:
            if self.constraint.get() and self.forced_board is not None:
                self.status_label.config(text=f"{self.current} の番 — 指定ミクロ盤: {self.forced_board + 1}")
            else:
                self.status_label.config(text=f"{self.current} の番 — 任意の未確定ミクロ盤に着手可")

    def _show_result_dialog(self, winner):
        dlg = tk.Toplevel(self.root)
        dlg.title("対局結果")
        dlg.transient(self.root)
        dlg.grab_set()
        dlg.resizable(False, False)

        if winner == 'draw':
            msg = "引き分けでした。再戦しますか？"
        else:
            msg = f"{winner} の勝ちです！再戦しますか？"

        tk.Label(dlg, text=msg, font=("Meiryo UI", 12)).pack(padx=16, pady=(16, 10))
        btns = tk.Frame(dlg)
        btns.pack(padx=16, pady=(0, 16))

        def on_rematch():
            dlg.destroy()
            self.new_game()

        def on_exit():
            dlg.destroy()
            self.root.destroy()

        tk.Button(btns, text="再戦", width=10, command=on_rematch).pack(side='left', padx=6)
        tk.Button(btns, text="終了", width=10, command=on_exit).pack(side='left', padx=6)

        dlg.protocol("WM_DELETE_WINDOW", on_rematch)

        dlg.update_idletasks()
        rw, rh = self.root.winfo_width(), self.root.winfo_height()
        rx, ry = self.root.winfo_rootx(), self.root.winfo_rooty()
        w, h = dlg.winfo_width(), dlg.winfo_height()
        if w <= 1 or h <= 1:
            w, h = dlg.winfo_reqwidth(), dlg.winfo_reqheight()
        x = rx + (rw - w) // 2
        y = ry + (rh - h) // 2
        dlg.geometry(f"+{max(x, 0)}+{max(y, 0)}")
        dlg.focus_set()

    def new_game(self):
        self.boards = [[' '] * 9 for _ in range(9)]
        self.micro_winner = [None] * 9
        self.current = '○'
        self.forced_board = None
        self.macro_winner_line = None
        for idx, btns in enumerate(self.micro_buttons):
            # オーバーレイがあれば除去
            if hasattr(self, 'micro_overlays') and self.micro_overlays[idx] is not None:
                try:
                    self.micro_overlays[idx].destroy()
                except Exception:
                    pass
                self.micro_overlays[idx] = None
            # ボタンを復元
            for b in btns:
                b.config(text=' ', state='normal', bg=self.root.cget('bg'))
                try:
                    b.grid()
                except Exception:
                    pass
            self.micro_frames[idx].config(bg=self._default_frame_bg)
        self._update_status()
        self._highlight_allowed()


def main():
    root = tk.Tk()
    app = UltimateTicTacToeGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
