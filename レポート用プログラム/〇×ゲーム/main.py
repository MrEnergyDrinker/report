import tkinter as tk


class TicTacToeGUI:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("3x3 ○×ゲーム - GUI")

        # ゲーム状態
        self.board = [' '] * 9
        self.current = '○'  # 先手
        self.ai_mark = '×'   # CPUが担当（CPU対戦時）
        self.winner_line = None
        self.vs_cpu = tk.BooleanVar(value=False)  # 初期は対人戦

        # スコア
        self.scores = {'○': 0, '×': 0, 'draw': 0}

        # UI 構築
        self._build_ui()
        self._update_status()

    def _build_ui(self):
        ctrl = tk.Frame(self.root)
        ctrl.pack(padx=10, pady=(10, 4), fill='x')

        tk.Checkbutton(ctrl, text="CPU対戦（×がCPU）", variable=self.vs_cpu,
                       command=self._on_toggle_mode).pack(side='left')
        tk.Button(ctrl, text="スコアリセット", command=self.reset_scores).pack(side='left', padx=6)

        score = tk.Frame(self.root)
        score.pack(padx=10, pady=(0, 6), fill='x')
        self.score_o = tk.Label(score, text="○: 0")
        self.score_x = tk.Label(score, text="×: 0")
        self.score_d = tk.Label(score, text="引き分け: 0")
        self.score_o.pack(side='left', padx=(0, 12))
        self.score_x.pack(side='left', padx=(0, 12))
        self.score_d.pack(side='left')

        board_frame = tk.Frame(self.root)
        board_frame.pack(padx=10, pady=6)
        self.buttons = []
        for r in range(3):
            for c in range(3):
                idx = r * 3 + c
                b = tk.Button(board_frame, text=' ', width=4, height=2,
                               font=("Meiryo UI", 28),
                               command=lambda i=idx: self.on_click(i))
                b.grid(row=r, column=c, padx=3, pady=3, sticky='nsew')
                self.buttons.append(b)

        status = tk.Frame(self.root)
        status.pack(padx=10, pady=(0, 10), fill='x')
        self.status_label = tk.Label(status, text="", anchor='w')
        self.status_label.pack(fill='x')

    def _on_toggle_mode(self):
        # モード変更時は新しい対局
        self.new_game()

    def on_click(self, idx: int):
        if self.board[idx] != ' ' or self.winner_line is not None:
            return
        self._place(idx, self.current)

        win = self._check_winner(self.current)
        if win:
            self._finish_game(winner=self.current, line=win)
            return
        if self._is_draw():
            self._finish_game(winner='draw', line=None)
            return

        self._switch_player()

        if self.vs_cpu.get() and self.current == self.ai_mark and self.winner_line is None:
            # 少し間を空けてCPUが指す
            self.root.after(150, self._cpu_move)

    def _cpu_move(self):
        if self.winner_line is not None:
            return
        idx = self._best_move(self.ai_mark)
        self._place(idx, self.ai_mark)

        win = self._check_winner(self.ai_mark)
        if win:
            self._finish_game(winner=self.ai_mark, line=win)
            return
        if self._is_draw():
            self._finish_game(winner='draw', line=None)
            return

        self._switch_player()

    def _place(self, idx: int, mark: str):
        self.board[idx] = mark
        self.buttons[idx].config(text=mark)

    def _switch_player(self):
        self.current = '×' if self.current == '○' else '○'
        self._update_status()

    def _update_status(self):
        if self.winner_line is None:
            mode = "CPU対戦" if self.vs_cpu.get() else "対人戦"
            ai_note = "（×=CPU）" if self.vs_cpu.get() else ""
            self.status_label.config(text=f"{mode}{ai_note} — {self.current} の番です")

    def _finish_game(self, winner, line):
        self.winner_line = line
        if line:
            for i in line:
                self.buttons[i].config(bg="#c7f5d9")
        if winner == 'draw':
            self.status_label.config(text="引き分けです。結果ダイアログで再戦を選べます。")
        else:
            self.status_label.config(text=f"{winner} の勝ちです！結果ダイアログで再戦を選べます。")
        # スコア更新と盤面無効化
        self.scores[winner] += 1
        self._update_scores()
        self._set_board_enabled(False)
        # 結果ダイアログ表示（再戦／終了）
        self._show_result_dialog(winner)

    def _update_scores(self):
        self.score_o.config(text=f"○: {self.scores['○']}")
        self.score_x.config(text=f"×: {self.scores['×']}")
        self.score_d.config(text=f"引き分け: {self.scores['draw']}")

    def _set_board_enabled(self, enabled: bool):
        for b in self.buttons:
            b.config(state=('normal' if enabled else 'disabled'))

    def new_game(self):
        self.board = [' '] * 9
        self.current = '○'
        self.winner_line = None
        for i, b in enumerate(self.buttons):
            b.config(text=' ', bg=self.root.cget('bg'))
        self._set_board_enabled(True)
        self._update_status()

    def reset_scores(self):
        self.scores = {'○': 0, '×': 0, 'draw': 0}
        self._update_scores()

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

        # 閉じるボタンは再戦と同じ動作にしておく
        dlg.protocol("WM_DELETE_WINDOW", on_rematch)

        # 中央に配置
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

    # 判定系
    @staticmethod
    def _winning_lines():
        return [
            (0, 1, 2), (3, 4, 5), (6, 7, 8),  # rows
            (0, 3, 6), (1, 4, 7), (2, 5, 8),  # cols
            (0, 4, 8), (2, 4, 6)              # diagonals
        ]

    def _check_winner(self, mark):
        for a, b, c in self._winning_lines():
            if self.board[a] == self.board[b] == self.board[c] == mark:
                return (a, b, c)
        return None

    def _is_draw(self):
        return all(cell != ' ' for cell in self.board)

    # CPU 思考（簡易）
    def _best_move(self, ai_mark: str) -> int:
        human = '○' if ai_mark == '×' else '×'
        empty = [i for i, v in enumerate(self.board) if v == ' ']

        # 1) 勝てるなら勝つ
        for i in empty:
            self.board[i] = ai_mark
            if self._check_winner(ai_mark):
                self.board[i] = ' '
                return i
            self.board[i] = ' '

        # 2) 負けそうならブロック
        for i in empty:
            self.board[i] = human
            if self._check_winner(human):
                self.board[i] = ' '
                return i
            self.board[i] = ' '

        # 3) 中央
        if 4 in empty:
            return 4

        # 4) 角
        for i in [0, 2, 6, 8]:
            if i in empty:
                return i

        # 5) 辺
        return empty[0]


def main():
    root = tk.Tk()
    app = TicTacToeGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
