# === このファイルの責務（GPT用構造補助） ===
# 本ファイルは「UI上でマッピングルールを選択・適用する」責務を担う
# 保存処理は mapping_processor.py 内で行われ、本モジュールは保存機能を持たない

import pandas as pd
import csv
import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import sys
import mapping_processor

# circusDB_viewer_edit.py ファイルのパスを追加
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def apply_mapping(company_db_path, mapping_path):
    """企業db.csv をマッピングしてデータを返す（保存しない）"""
    try:
        df_company = pd.read_csv(company_db_path, encoding="utf-8-sig")
        with open(mapping_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            mapping_data = list(reader)

        mapped_rows = []
        for _, row in df_company.iterrows():
            rules = [
                rule for rule in mapping_data
                if rule['企業名'] == row['企業名'] and row['管理番号の文字列'] and row['管理番号'].startswith(rule['管理番号の文字列'])
            ]
            if rules:
                rule = rules[0]
                new_data = {}
                for circus_col in rule:
                    company_col_template = rule.get(circus_col)
                    if company_col_template:
                        try:
                            new_data[circus_col] = company_col_template.format(**row)
                        except KeyError:
                            new_data[circus_col] = ""
                    else:
                        new_data[circus_col] = ""
                mapped_rows.append(new_data)

        return pd.DataFrame(mapped_rows)
    except Exception as e:
        messagebox.showerror("エラー", f"マッピング処理でエラーが発生しました: {e}")
        return pd.DataFrame()

class MappingToolUI(tk.Frame):
    def __init__(self, parent, circus_db_path, mapping_path):
        super().__init__(parent)
        self.circus_db_path = circus_db_path
        self.mapping_path = mapping_path
        self.company_data = {}
        self.load_company_data()
        self.create_widgets()
        self.entries = {}
        self.rules = []

    def load_company_data(self):
        try:
            df = pd.read_csv("企業管理DB.csv", encoding="utf-8-sig")
            for _, row in df.iterrows():
                self.company_data[row["企業名"]] = row["識別アルファベット"]
        except FileNotFoundError:
            print("Error: '企業管理DB.csv' が見つかりません。")
        except Exception as e:
            print(f"Error: 企業名と識別アルファベットの読み込み中にエラー: {e}")

    def create_widgets(self):
        tk.Label(self, text="企業名:").grid(row=0, column=0, padx=5, pady=5)
        self.company_entry = ttk.Combobox(self, values=list(self.company_data.keys()), width=30)
        self.company_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(self, text="管理番号の文字列:").grid(row=1, column=0, padx=5, pady=5)
        self.management_number_entry = ttk.Combobox(self, values=list(self.company_data.values()), width=30)
        self.management_number_entry.grid(row=1, column=1, padx=5, pady=5)

        tk.Button(self, text="企業db選択ボタン", command=self.select_company_db).grid(row=2, column=0, columnspan=2, padx=5, pady=5)

        self.selected_file_label = tk.Label(self, text="選択されたファイル:")
        self.selected_file_label.grid(row=3, column=0, columnspan=2, pady=5)

        self.preview_notebook = ttk.Notebook(self, width=1200, height=500)
        self.preview_notebook.grid(row=4, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")

    def show_preview(self, company_name, management_number):
        for tab_id in self.preview_notebook.tabs():
            self.preview_notebook.forget(tab_id)

        self.rules = mapping_processor.load_mapping_rules(self.mapping_path, company_name, management_number)

        from circusDB_viewer_edit import CircusDB_viewer_edit

        for i, rule in enumerate(self.rules):
            tab_frame = tk.Frame(self.preview_notebook)
            self.preview_notebook.add(tab_frame, text=f"ルール {i + 1}")

            preview_viewer = CircusDB_viewer_edit(tab_frame)
            preview_viewer.pack(fill=tk.BOTH, expand=True)

            self.set_preview_data(preview_viewer, company_name, management_number, rule)

        tk.Button(self, text="このルールを保存する", command=self.confirm_rule).grid(row=6, column=0, columnspan=2, pady=10)

    def set_preview_data(self, preview_viewer, company_name, management_number, rule):
        from circusDB_viewer_edit import CircusDB_viewer_edit
        company_db_file = f"{company_name}_db.csv"
        company_db_path = os.path.join("data", company_db_file)

        try:
            df_company = pd.read_csv(company_db_path, encoding="utf-8-sig")

            preview_data = {}
            for circus_col, company_col_template in rule.items():
                if company_col_template:
                    try:
                        preview_data[circus_col] = company_col_template.format(**df_company.iloc[0])
                    except KeyError:
                        preview_data[circus_col] = ""
                else:
                    preview_data[circus_col] = ""

            for field, value in preview_data.items():
                if field in preview_viewer.entries:
                    entry = preview_viewer.entries[field]
                    entry.delete("1.0", tk.END)
                    entry.insert("1.0", value)
        except FileNotFoundError as e:
            messagebox.showerror("エラー", f"ファイルが見つかりません: {e}")
        except Exception as e:
            messagebox.showerror("エラー", f"プレビュー設定中にエラー: {e}")

    def select_company_db(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if file_path:
            self.selected_file_label.config(text=f"選択されたファイル: {file_path}")
            self.show_preview(self.company_entry.get(), self.management_number_entry.get())

    def confirm_rule(self):
        company_name = self.company_entry.get()
        management_number = self.management_number_entry.get()
        company_db_file = f"{company_name}_db.csv"
        company_db_path = os.path.join("data", company_db_file)

        selected_tab_index = self.preview_notebook.index(self.preview_notebook.select())

        try:
            mapping_processor.execute_mapping_with_rules(
                company_name, management_number, self.rules, company_db_path, selected_tab_index
            )
        except mapping_processor.MappingError as e:
            messagebox.showerror("エラー", f"マッピング中にエラーが発生しました: {e}")

def load_mapping_rules(mapping_path, company_name, management_number):
    mapping_rules = []
    try:
        with open(mapping_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['企業名'] == company_name and row['管理番号の文字列'] == management_number:
                    mapping_rules.append({
                        col: row[col] for col in reader.fieldnames if col not in ["No.", "企業名", "管理番号の文字列"]
                    })
    except FileNotFoundError:
        print("circus_db_mapping.csv が見つかりません。")
    except Exception as e:
        print(f"Error loading mapping rules: {e}")
    return mapping_rules
