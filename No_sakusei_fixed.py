import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import pandas as pd
import csv


class Company:
    def __init__(self, name, address="", phone=""):
        self.name = name
        self.address = address
        self.phone = phone
        self.id = None


class IdGenerator:
    def __init__(self, company_id_prefix="ABC"):
        self.company_id_prefix = company_id_prefix
        self.counter = 1

    def generate_id(self, format_type="normal", derivation_type="無", derivation_count=0):
        if format_type == "normal":
            id_str = f"{self.company_id_prefix}{self.counter}"
        # elif format_type == "rule_based":  # ルールベースのID生成は削除
        #     # ... (ルールベースのID生成処理は削除) ...
        else:  # その他（ここでは通常のID生成と同じ）
            id_str = f"{self.company_id_prefix}{self.counter}"

        if derivation_type == "有":
            id_str += f"_{derivation_count}"  # 派生数があれば追加

        self.counter += 1
        return id_str


class InputUI:
    def __init__(self, master, id_generator):
        self.master = master
        self.id_generator = id_generator
        self.company_db_file_path = "企業管理DB.csv"
        self.df_company_db = None
        self.company_names = []

        if hasattr(master, "title"):
            master.title("企業情報入力")

        self.create_widgets()
        self.load_company_data_from_csv()

    def create_widgets(self):
        # 企業名入力 (ドロップリスト)
        self.name_label = tk.Label(self.master, text="企業名:")
        self.name_label.grid(row=0, column=0)
        self.name_var = tk.StringVar()
        self.name_dropdown = ttk.Combobox(
            self.master, textvariable=self.name_var, values=self.company_names)
        self.name_dropdown.grid(row=0, column=1)
        self.name_dropdown.bind(
            "<<ComboboxSelected>>", self.load_company_data)

        # 識別アルファベット入力
        self.alphabet_label = tk.Label(self.master, text="識別アルファベット:")
        self.alphabet_label.grid(row=1, column=0)
        self.alphabet_entry = tk.Entry(self.master)
        self.alphabet_entry.grid(row=1, column=1)

        # 番号生成タイプ選択
        self.format_type_label = tk.Label(self.master, text="番号生成タイプ:")
        self.format_type_label.grid(row=2, column=0)
        self.format_type_var = tk.StringVar(value="normal")
        self.format_type_radio1 = tk.Radiobutton(
            self.master, text="通常", variable=self.format_type_var, value="通常")
        self.format_type_radio1.grid(row=2, column=1)
        self.format_type_radio2 = tk.Radiobutton(
            self.master, text="その他", variable=self.format_type_var, value="その他")  # その他に戻す
        self.format_type_radio2.grid(row=3, column=1)

        # 派生タイプ選択
        self.derivation_type_label = tk.Label(self.master, text="派生タイプ:")
        self.derivation_type_label.grid(row=4, column=0)  # 行番号を調整
        self.derivation_type_var = tk.StringVar(value="無")
        self.derivation_type_radio1 = tk.Radiobutton(
            self.master, text="無", variable=self.derivation_type_var, value="無")
        self.derivation_type_radio1.grid(row=4, column=1)  # 行番号を調整
        self.derivation_type_radio2 = tk.Radiobutton(
            self.master, text="有", variable=self.derivation_type_var, value="有")
        self.derivation_type_radio2.grid(row=5, column=1)  # 行番号を調整

        # 派生数入力
        self.derivation_count_label = tk.Label(self.master, text="派生数:")
        self.derivation_count_label.grid(row=6, column=0)  # 行番号を調整
        self.derivation_count_entry = tk.Entry(
            self.master, state="disabled")  # 初期状態は無効
        self.derivation_count_entry.grid(row=6, column=1)  # 行番号を調整

        # 登録ボタン
        self.submit_button = tk.Button(
            self.master, text="登録", command=self.submit)
        self.submit_button.grid(row=7, column=1)  # 行番号を調整

        # 派生タイプラジオボタンのコールバックを設定
        self.derivation_type_var.trace(
            "w", self.update_derivation_count_entry_state)

    def update_derivation_count_entry_state(self, *args):
        """派生タイプに応じて派生数入力欄の状態を更新する"""
        if self.derivation_type_var.get() == "有":
            self.derivation_count_entry.config(state="normal")
        else:
            self.derivation_count_entry.config(state="disabled")

    def load_company_data_from_csv(self):
        try:
            if os.path.exists(self.company_db_file_path):
                self.df_company_db = pd.read_csv(self.company_db_file_path)
                self.company_names = self.df_company_db["企業名"].unique(
                ).tolist()
                self.name_dropdown['values'] = self.company_names
            else:
                self.df_company_db = pd.DataFrame(columns=[
                                                   "企業名", "識別アルファベット", "番号生成タイプ", "派生タイプ", "派生数"])
                messagebox.showwarning(
                    "CSVファイルが見つかりません", f"{self.company_db_file_path} が見つかりません。新規作成します。")
        except Exception as e:
            messagebox.showerror(
                "エラー", f"CSVの読み込み中にエラーが発生しました: {e}")

    def load_company_data(self, event=None):
        selected_company = self.name_var.get()
        if selected_company in self.df_company_db["企業名"].values:
            company_data = self.df_company_db[self.df_company_db["企業名"]
                                            == selected_company].iloc[0]
            self.alphabet_entry.delete(0, tk.END)
            self.alphabet_entry.insert(
                0, company_data["識別アルファベット"])
            self.format_type_var.set(company_data["番号生成タイプ"])
            # 派生タイプと派生数を設定
            derivation_type = company_data["派生タイプ"]
            self.derivation_type_var.set(derivation_type)
            if derivation_type == "有":
                derivation_count = company_data["派生数"]
                self.derivation_count_entry.config(state="normal")
                self.derivation_count_entry.delete(0, tk.END)
                self.derivation_count_entry.insert(0, derivation_count)
            else:
                self.derivation_count_entry.config(state="disabled")
                self.derivation_count_entry.delete(0, tk.END)

    def submit(self):
        company_name = self.name_var.get()
        alphabet = self.alphabet_entry.get()
        format_type = self.format_type_var.get()
        derivation_type = self.derivation_type_var.get()
        derivation_count_str = self.derivation_count_entry.get()
        
        # 派生数が数値かどうかをチェック
        if derivation_type == "有" and not derivation_count_str.isdigit():
            messagebox.showerror("エラー", "派生数は数値で入力してください。")
            return
        
        derivation_count = int(derivation_count_str) if derivation_type == "有" else 0

        if not company_name or not alphabet:
            messagebox.showerror(
                "エラー", "企業名と識別アルファベットを入力してください。")
            return

        if company_name in self.df_company_db["企業名"].values:
            try:
                df = pd.read_csv(self.company_db_file_path)
                company_index = df[df["企業名"] == company_name].index[0]
                df.loc[company_index,
                       "識別アルファベット"] = alphabet
                df.loc[company_index, "番号生成タイプ"] = format_type
                df.loc[company_index, "派生タイプ"] = derivation_type
                df.loc[company_index, "派生数"] = derivation_count
                df.to_csv(self.company_db_file_path,
                          index=False, encoding="utf-8-sig")
                messagebox.showinfo("更新完了", f"企業情報が更新されました。")
            except Exception as e:
                messagebox.showerror(
                    "エラー", f"企業情報の更新中にエラーが発生しました: {e}")
        else:
            company = Company(company_name)
            company.id = self.id_generator.generate_id(
                format_type, derivation_type, derivation_count)
            messagebox.showinfo("登録完了", f"企業ID: {company.id}")
            self.company_names.append(company_name)
            self.name_dropdown['values'] = self.company_names
            new_row = pd.DataFrame([[company_name, alphabet, format_type, derivation_type, derivation_count]],
                                    columns=["企業名", "識別アルファベット", "番号生成タイプ", "派生タイプ", "派生数"])
            self.df_company_db = pd.concat(
                [self.df_company_db, new_row], ignore_index=True)
            self.df_company_db.to_csv(self.company_db_file_path,
                                     index=False, encoding="utf-8-sig")


# メイン処理
if __name__ == "__main__":
    root = tk.Tk()
    id_generator = IdGenerator()
    ui = InputUI(root, id_generator)
    root.mainloop()
