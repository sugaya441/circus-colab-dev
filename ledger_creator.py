import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

class LedgerCreatorApp:
    def __init__(self, root):
        self.root = root
        self.circus_file = ""
        self.company_file = ""
        self.circus_df = None
        self.company_df = None

        # メインフレーム（ファイル選択）
        frame1 = tk.LabelFrame(root, text="ファイル選択", padx=10, pady=10)
        frame1.pack(fill="x", padx=10, pady=5)

        tk.Button(frame1, text="Circus DB を選択", command=self.select_circus_file).pack(side="left", padx=5)
        tk.Button(frame1, text="企業 DB を選択", command=self.select_company_file).pack(side="left", padx=5)

        # **選択可能な項目リスト**
        frame2 = tk.LabelFrame(root, text="選択可能な項目", padx=10, pady=10)
        frame2.pack(fill="both", expand=True, padx=10, pady=5)

        self.available_tree = ttk.Treeview(frame2, columns=("項目名", "プレースホルダー", "データ元"), show="headings")
        self.available_tree.heading("項目名", text="項目名")
        self.available_tree.heading("プレースホルダー", text="プレースホルダー")
        self.available_tree.heading("データ元", text="データ元")

        self.available_tree.pack(fill="both", expand=True)
        self.available_tree.bind_all("<MouseWheel>", lambda event: self.available_tree.yview_scroll(int(-1*(event.delta/120)), "units"))
        tk.Button(frame2, text="▼ 項目を追加 ▼", command=self.add_selected_column).pack(fill="x", pady=5)

        # **選択済みの項目リスト**
        frame3 = tk.LabelFrame(root, text="台帳の項目（並び替え可能）", padx=10, pady=10)
        frame3.pack(fill="both", expand=True, padx=10, pady=5)

        self.tree = ttk.Treeview(frame3, columns=("項目名", "データ元"), show="headings")
        self.tree.heading("項目名", text="項目名")
        self.tree.heading("データ元", text="データ元")

        self.tree.pack(fill="both", expand=True)
        self.tree.bind_all("<MouseWheel>", lambda event: self.tree.yview_scroll(int(-1*(event.delta/120)), "units"))

        # **並び替えボタン**
        btn_frame = tk.Frame(root)
        btn_frame.pack(fill="x", padx=10, pady=5)

        tk.Button(btn_frame, text="🔼 上へ", command=self.move_up).pack(side="left", padx=5)
        tk.Button(btn_frame, text="🔽 下へ", command=self.move_down).pack(side="left", padx=5)

        # **台帳作成 & 終了ボタン**
        frame4 = tk.Frame(root)
        frame4.pack(fill="x", padx=10, pady=5)

        tk.Button(frame4, text="📄 台帳を作成", command=self.create_ledger).pack(side="left", padx=5)
        tk.Button(frame4, text="❌ 終了", command=self.exit_app).pack(side="right", padx=5)

        # **台帳プレビュー（実際の台帳データを表示）**
        frame5 = tk.LabelFrame(root, text="台帳プレビュー（実際のデータ）", padx=10, pady=10)
        frame5.pack(fill="both", expand=True, padx=10, pady=5)

        self.preview_tree = ttk.Treeview(frame5, show="headings")
        self.preview_tree.pack(fill="both", expand=True)
        self.preview_tree.bind_all("<MouseWheel>", lambda event: self.preview_tree.yview_scroll(int(-1*(event.delta/120)), "units"))

    def exit_app(self):
        """アプリを終了"""
        self.root.quit()

    def select_circus_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if file_path:
            self.circus_file = file_path
            self.circus_df = pd.read_csv(file_path, encoding="utf-8-sig")
            self.load_column_selection()

    def select_company_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if file_path:
            self.company_file = file_path
            self.company_df = pd.read_csv(file_path, encoding="utf-8-sig")
            self.load_column_selection()

    def load_column_selection(self):
        if self.circus_df is None or self.company_df is None:
            return

        self.available_tree.delete(*self.available_tree.get_children())

        for col in self.circus_df.columns:
            placeholder = f"{self.circus_df[col].iloc[0]}" if not pd.isna(self.circus_df[col].iloc[0]) else "{空欄}"
            self.available_tree.insert("", "end", values=(col, placeholder, "CircusDB"))

        for col in self.company_df.columns:
            placeholder = f"{self.company_df[col].iloc[0]}" if not pd.isna(self.company_df[col].iloc[0]) else "{空欄}"
            self.available_tree.insert("", "end", values=(col, placeholder, "企業DB"))

    def add_selected_column(self):
        selected_items = [self.available_tree.item(item)["values"] for item in self.available_tree.selection()]
        for item in selected_items:
            if not any(self.tree.item(child)["values"][0] == item[0] for child in self.tree.get_children()):
                self.tree.insert("", "end", values=(item[0], item[2]))

        self.update_preview()

    def create_ledger(self):
        """台帳を作成し、Excel / CSV に保存"""
        selected_columns = [self.tree.item(item)["values"][0] for item in self.tree.get_children()]
        if not selected_columns:
            messagebox.showwarning("警告", "台帳に項目が追加されていません。")
            return

        if self.circus_df is None or self.company_df is None:
            messagebox.showwarning("警告", "DBファイルが選択されていません。")
            return

        # **管理番号をキーにデータを結合**
        merged_df = pd.merge(self.circus_df, self.company_df, on="管理番号", how="left")

        # **選択された項目だけを抽出**
        try:
            ledger_df = merged_df[selected_columns]
        except KeyError:
            messagebox.showerror("エラー", "選択された項目の一部が存在しません。")
            return

        # **ファイル保存ダイアログ**
        file_path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excelファイル", "*.xlsx"), ("CSVファイル", "*.csv")],
            title="台帳を保存"
        )

        # **ユーザーがキャンセルした場合は処理を中断**
        if not file_path:
            messagebox.showwarning("警告", "ファイル保存がキャンセルされました。")
            return

        try:
            if file_path.endswith(".xlsx"):
                ledger_df.to_excel(file_path, index=False)
            else:
                ledger_df.to_csv(file_path, index=False, encoding="utf-8-sig")
        
            messagebox.showinfo("保存完了", f"管理台帳を {file_path} に保存しました")
        except Exception as e:
            messagebox.showerror("エラー", f"ファイルの保存に失敗しました:\n{str(e)}")

    def move_up(self):
        """台帳の項目を上へ移動"""
        selected = self.tree.selection()
        for item in selected:
            index = self.tree.index(item)
            if index > 0:
                self.tree.move(item, "", index - 1)

    def move_down(self):
        """台帳の項目を下へ移動"""
        selected = self.tree.selection()
        for item in reversed(selected):
            index = self.tree.index(item)
            if index < len(self.tree.get_children()) - 1:
                self.tree.move(item, "", index + 1)

    def update_preview(self):
        """実際に作成される台帳のプレビューを表示"""
        selected_columns = [self.tree.item(item)["values"][0] for item in self.tree.get_children()]
        if self.circus_df is None or self.company_df is None:
            return
        
        merged_df = pd.merge(self.circus_df, self.company_df, on="管理番号", how="left")
        preview_df = merged_df[selected_columns]

        self.preview_tree["columns"] = selected_columns
        self.preview_tree["show"] = "headings"

        for col in selected_columns:
            self.preview_tree.heading(col, text=col)
            self.preview_tree.column(col, width=150)

        self.preview_tree.delete(*self.preview_tree.get_children())
        for _, row in preview_df.iterrows():
            self.preview_tree.insert("", "end", values=row.tolist())

if __name__ == "__main__":
    root = tk.Tk()
    app = LedgerCreatorApp(root)
    root.mainloop()
