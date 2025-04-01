##mapping_tool.py (リファクタリング後)

import tkinter as tk
from tkinter import messagebox, filedialog
from tkinter import ttk
import pandas as pd
import os
import csv
import datetime

# === 1. 初期設定 & データ管理 ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(BASE_DIR)
CIRCUS_DB_FILE = os.path.join(BASE_DIR, "circus_db.csv")
MAPPING_FILE = os.path.join(BASE_DIR, "circus_db_mapping.csv")
BACKUP_DIR = os.path.join(BASE_DIR, "backup")
os.makedirs(BACKUP_DIR, exist_ok=True)

df_company = None  # 企業DBデータのグローバル変数

def load_company_names(csv_path="企業管理DB.csv"):
    """企業管理DB.csvから企業名を取得"""
    try:
        df = pd.read_csv(csv_path, encoding="utf-8")
        return df["企業名"].dropna().unique().tolist()
    except FileNotFoundError:
        return []
    except Exception as e:
        print(f"企業名読み込みエラー: {e}")
        return []

def load_company_db():
    """企業DBを読み込む"""
    global df_company
    file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
    if not file_path:
        return
    df_company = pd.read_csv(file_path, encoding='utf-8-sig')
    messagebox.showinfo("成功", "企業DBを読み込みました。")

def get_company_list():
    """dataフォルダ内の企業リストを取得"""
    data_dir = os.path.join(BASE_DIR, "data")
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    return [f.replace(".csv", "") for f in os.listdir(data_dir) if f.endswith(".csv")]

# === 2. マッピングデータ管理 ===
class MappingTool(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.mapping_cache = {}
        self.next_no = 1
        self.load_mapping_from_file()
        self.create_main_window()

    def load_mapping_from_file(self):
        """保存を含まない読み込み専用関数"""
        if os.path.exists(MAPPING_FILE):
            try:
                with open(MAPPING_FILE, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        no = int(row.get('No.', 0) or 0)
                        company_name = row.get('企業名', '')
                        management_number = row.get('管理番号の文字列', '')
                        data = {k: v for k, v in row.items() if k not in ['No.', '企業名', '管理番号の文字列']}
                        self.mapping_cache[no] = {
                            'No.': no, '企業名': company_name, '管理番号の文字列': management_number
                        }
                        self.mapping_cache[no].update(data)
                        self.next_no = max(self.next_no, no + 1)
            except Exception as e:
                print(f"Error loading mapping: {e}")
                messagebox.showerror("エラー", f"読み込みエラーが発生しました: {e}")
    def save_mapping_to_file(self):
        import os
        import pandas as pd
        from data_saver import save_circus_db

        target_csv = 'circus_db_mapping.csv'
        existing_df = pd.read_csv(target_csv) if os.path.exists(target_csv) else pd.DataFrame()

        # 保存対象：キャッシュからのルール抽出
        new_entries = []
        for entry in self.mapping_cache.values():
            if isinstance(entry, dict):
                new_entries.append(entry)
        new_df = pd.DataFrame(new_entries)

        # 必須キーがない場合エラー
        if '企業名' not in new_df.columns or '管理番号' not in new_df.columns:
            print("[保存エラー] '企業名'または'管理番号'列が存在しません")
            return

        # 上書き対象だけ除外して結合（他は保持）
        if not existing_df.empty:
            target_keys = set(zip(new_df['企業名'], new_df['管理番号']))
            keep_df = existing_df[~existing_df.apply(lambda row: (row['企業名'], row['管理番号']) in target_keys, axis=1)]
            merged_df = pd.concat([keep_df, new_df], ignore_index=True)
        else:
            merged_df = new_df.copy()

        # 保存
        save_circus_db(merged_df)
        print("[保存完了] マッピングルールを保存しました")

        headers = [
            "No.", "企業名", "管理番号の文字列",
            "求人タイトル", "募集予定人数", "仕事内容", "PRポイント", "募集概要_資料",
            "勤務地住所", "勤務時間補足", "勤務地・勤務時間_資料",
            "年収例", "給与条件補足", "給与・賞与_資料",
            "休日休暇補足", "休日・休暇_資料",
            "福利厚生・諸手当", "福利厚生・諸手当_資料",
            "応募時必須条件", "求める人材_資料",
            "成果報酬金額", "支払いサイト", "返戻金規定", "手数料設定_資料"
        ]

        try:
            with open(MAPPING_FILE, 'w', encoding='utf-8-sig', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=headers)
                writer.writeheader()
                for no, data in sorted(self.mapping_cache.items()):
                    # BOMがついた `\ufeffNo.` を `No.` に変換
                    if "\ufeffNo." in data:
                        data["No."] = data.pop("\ufeffNo.")

                    writer.writerow(data)

            messagebox.showinfo("保存完了", "マッピングデータがファイルに正常に保存されました。")

        except Exception as e:
            print(f"Error saving mapping: {e}")
            messagebox.showerror("エラー", f"マッピングデータの保存中にエラーが発生しました: {e}")

    def save_mapping(self):
        """企業名と管理番号文字列を確定し、キャッシュに保存（既存データがあれば読み込む）"""
        company_name = self.company_entry.get()
        management_number = self.management_number_entry.get()

        if not company_name or not management_number:
            messagebox.showerror("エラー", "企業名と管理番号を入力してください。")
            return

        # 既存のデータを検索
        existing_no = None
        if os.path.exists(MAPPING_FILE):
            try:
                with open(MAPPING_FILE, 'r', encoding='utf-8-sig') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        # `No.` のキーが `\ufeffNo.` になっている場合、修正する
                        no_key = next((k for k in row.keys() if "No." in k), "No.")
                        
                        if row["企業名"] == company_name and row["管理番号の文字列"] == management_number:
                            existing_no = int(row[no_key])  # 修正したキーを使用
                            self.mapping_cache[existing_no] = row  # 既存データをキャッシュに保存
                            break
            except Exception as e:
                print(f"Error loading existing mapping: {e}")
                messagebox.showerror("エラー", f"既存データの読み込み中にエラーが発生しました: {e}")
                return

        # 既存データがある場合はそのデータを使用
        if existing_no is not None:
            no = existing_no
            messagebox.showinfo("データ取得", f"既存のデータを取得しました。（No. {no}）")
        else:
            no = self.next_no  # 既存データがなければ新しい `no` を割り当てる
            self.next_no += 1  # 次の `no` を更新
            self.mapping_cache[no] = {
                "No.": no,
                "企業名": company_name,
                "管理番号の文字列": management_number
            }
            messagebox.showinfo("保存", f"企業名と管理番号をキャッシュに保存しました。（No. {no}）")


        # ヘッダーリスト（save_mapping_to_file()と統一）
        headers = [
            "No.", "企業名", "管理番号の文字列",
            "求人タイトル", "募集予定人数", "仕事内容", "PRポイント", "募集概要_資料",
            "勤務地住所", "勤務時間補足", "勤務地・勤務時間_資料",
            "年収例", "給与条件補足", "給与・賞与_資料",
            "休日休暇補足", "休日・休暇_資料",
            "福利厚生・諸手当", "福利厚生・諸手当_資料",
            "応募時必須条件", "求める人材_資料",
            "成果報酬金額", "支払いサイト", "返戻金規定", "手数料設定_資料"
        ]

        # キャッシュに No., 企業名, 管理番号文字列, その他空の項目を用意
        if no not in self.mapping_cache:
            self.mapping_cache[no] = {key: "" for key in headers}  # 空データを設定
            self.mapping_cache[no]["No."] = no
            self.mapping_cache[no]["企業名"] = company_name
            self.mapping_cache[no]["管理番号の文字列"] = management_number            

        messagebox.showinfo("保存", f"企業名と管理番号をキャッシュに保存しました。（No. {no}）")

            
    def create_main_window(self):
        """メインウィンドウを作成"""
        tk.Label(self, text="マッピングツール", font=("Arial", 16)).pack(pady=10)

        # 上部にボタンと入力欄を横並びに配置
        top_frame = tk.Frame(self)
        top_frame.pack(fill=tk.X, padx=10, pady=5)

        # 企業DB読み込みボタン
        tk.Button(top_frame, text="企業DBを読み込み", command=load_company_db).pack(side=tk.LEFT, padx=5)

        # 企業名入力
        company_names = load_company_names()
        tk.Label(top_frame, text="企業名を入力:").pack(side=tk.LEFT,pady=5)
        self.company_entry = ttk.Combobox(top_frame, values=company_names, width=40)
        self.company_entry.pack(side=tk.LEFT, padx=5)
        self.company_entry.bind("<<ComboboxSelected>>", self.update_management_number_list)

        # 管理番号入力（ドロップダウンリスト＋手入力可能）
        tk.Label(top_frame, text="管理番号の文字列:").pack(side=tk.LEFT, padx=5)
        self.management_number_entry = ttk.Combobox(top_frame, values=[], width=15)
        self.management_number_entry.pack(side=tk.LEFT,padx=5)
        self.management_number_entry.set("新規入力可")  # デフォルトテキスト
        self.management_number_entry.bind("<KeyRelease>", self.allow_custom_management_number)

        # 企業名・管理番号確定ボタン
        tk.Button(top_frame, text="確定", command=self.save_mapping).pack(side=tk.LEFT, padx=5)

        # マッピングルール保存ボタン
        tk.Button(self, text="マッピングルール保存", command=self.save_mapping_to_file).pack(pady=5)

        self.create_blocks()  # ブロックの作成を呼び出す

    def update_management_number_list(self, event=None):
        """企業名を選択した際に、該当企業の管理番号をドロップダウンリストに反映"""
        company_name = self.company_entry.get()
        if not company_name or not os.path.exists(MAPPING_FILE):
            return

        try:
            management_numbers = set()  # 重複しないように管理
            with open(MAPPING_FILE, 'r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row["企業名"] == company_name:
                        management_numbers.add(row["管理番号の文字列"])

            self.management_number_entry["values"] = list(management_numbers) + ["新規入力可"]
        except Exception as e:
            print(f"Error updating management numbers: {e}")
            messagebox.showerror("エラー", "管理番号リストの更新中にエラーが発生しました。")

    def allow_custom_management_number(self, event=None):
        """管理番号の手入力を許可する（選択リストにない番号も入力可能）"""
        self.management_number_entry.set(self.management_number_entry.get())

    def get_current_no(self):
        """現在選択されている企業名と管理番号に紐づく No. を取得"""
        company_name = self.company_entry.get()
        management_number = self.management_number_entry.get()

        for existing_no, data in self.mapping_cache.items():
            if data["企業名"] == company_name and data["管理番号の文字列"] == management_number:
                return existing_no

        return None  # 見つからなかった場合は None を返す


    def create_blocks(self):
        """編集用ブロックを作成"""
        blocks = {
            "募集概要": ["求人タイトル", "募集予定人数", "仕事内容", "PRポイント", "募集概要_資料"],
            "勤務地・勤務時間": ["勤務地住所", "勤務時間補足", "勤務地・勤務時間_資料"],
            "給与・賞与": ["年収例", "給与条件補足", "給与・賞与_資料"],
            "休日・休暇": ["休日休暇補足", "休日・休暇_資料"],
            "福利厚生・諸手当": ["福利厚生・諸手当", "福利厚生・諸手当_資料"],
            "求める人材": ["応募時必須条件", "求める人材_資料"],
            "手数料設定": ["成果報酬金額", "支払いサイト", "返戻金規定", "手数料設定_資料"],
        }

        main_frame = tk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        for i, (block, fields) in enumerate(blocks.items()):
            frame = tk.LabelFrame(main_frame, text=block, padx=5, pady=5)
            frame.grid(row=i // 3, column=i % 3, padx=5, pady=5, sticky="nsew")
            for col in fields:
                tk.Button(frame, text=f"{col} を編集",
                          command=lambda c=col, n=self.get_current_no():
                          self.open_window_editor(c, n)).pack(pady=2)

    def open_window_editor(self, column_name, no=None):
        """文面編集ウィンドウを開く"""
        if no is None:
            no = self.get_current_no()  # **修正: 現在のNo.を正しく取得**

        if no is None:
            messagebox.showerror("エラー", "企業名と管理番号が未入力、または正しく確定されていません。")
            return

        if no not in self.mapping_cache:
            self.mapping_cache[no] = {}

        edit_window = tk.Toplevel()
        edit_window.title(f"{column_name} - 文面作成 / 編集")
        edit_window.geometry("700x500")

        tk.Label(edit_window, text="プレビュー:").pack(pady=5)
        preview_text = tk.Text(edit_window, height=8, wrap="word")
        preview_text.pack(padx=10, pady=5, expand=True, fill="both")

        tk.Label(edit_window, text="文面編集:").pack(pady=5)
        edit_text = tk.Text(edit_window, height=10, wrap="word")

        # **修正: キャッシュされたNo.のデータを正しく取得**
        existing_text = self.mapping_cache.get(no, {}).get(column_name, "")
        edit_text.insert("1.0", existing_text)
        edit_text.pack(padx=10, pady=5, expand=True, fill="both")

        # 🔹 修正: `update_preview()` を追加し、ウィンドウを開いた時点でプレビューを更新
        self.update_preview(edit_text, preview_text)

        # 🔹 修正: テキスト編集時にプレビューをリアルタイム更新
        edit_text.bind("<KeyRelease>", lambda event: self.update_preview(edit_text, preview_text))

        dropdown_frame = tk.Frame(edit_window)
        dropdown_frame.pack(pady=10)

        tk.Label(dropdown_frame, text="挿入する企業DB項目").grid(row=0, column=0, padx=5)

        # **修正: df_companyがNoneの場合は空リストをセット**
        column_list = list(df_company.columns) if df_company is not None else []
        item_name_selector = ttk.Combobox(dropdown_frame, values=column_list, width=30)
        item_name_selector.grid(row=0, column=1, padx=5)

        def insert_item_name():
            item_name = item_name_selector.get()
            if item_name:
                edit_text.insert(tk.INSERT, f"{{{item_name}}}")
                update_preview()

        tk.Button(dropdown_frame, text="項目を挿入", command=insert_item_name).grid(row=1, column=1, padx=5)
        save_button = tk.Button(edit_window, text="保存", command=lambda: self.save_changes(column_name, edit_text, preview_text, edit_window))
        save_button.pack(pady=10)

    def update_preview(self, edit_text, preview_text):
        """プレビュー画面を更新"""
        try:
            if df_company is not None and not df_company.empty:
                test_data = df_company.iloc[0].to_dict()
            else:
                test_data = {}

            raw_text = edit_text.get("1.0", tk.END).strip()
            formatted_text = raw_text.format(**test_data)

            preview_text.delete("1.0", tk.END)
            preview_text.insert("1.0", formatted_text if formatted_text else "データがありません。")
        except KeyError as e:
            preview_text.delete("1.0", tk.END)
            preview_text.insert("1.0", f"プレビューの更新中にキーエラーが発生しました: {e}")
        except Exception as e:
            preview_text.delete("1.0", tk.END)
            preview_text.insert("1.0", "プレビューの更新中にエラーが発生しました。")

    def save_changes(self, column_name, edit_text, preview_text, edit_window):
        """キャッシュにデータを保存し、保持しているキャッシュNo.に追記"""
        correct_no = self.get_current_no()  # **修正: 最新のNo.を取得**

        if correct_no is None:
            messagebox.showerror("エラー", "企業名と管理番号を確定してください。")
            return

        if correct_no not in self.mapping_cache:
            self.mapping_cache[correct_no] = {}

        # 既存データを保持しながら追記
        existing_text = self.mapping_cache[correct_no].get(column_name, "")
        new_text = edit_text.get("1.0", tk.END).strip()
        
        if existing_text:
            self.mapping_cache[correct_no][column_name] = existing_text + "\n" + new_text
        else:
            self.mapping_cache[correct_no][column_name] = new_text

        messagebox.showinfo("保存完了", f"{column_name} の内容をキャッシュに追記しました。（No. {correct_no}）")

        # 🔹 修正: 保存後に `update_preview()` を呼び出してプレビューを更新
        self.update_preview(edit_text, preview_text)

        edit_window.destroy()

        
    @staticmethod
    def add_to_tab(parent_notebook):
        """タブにマッピングツールを追加"""
        frame = ttk.Frame(parent_notebook)
        parent_notebook.add(frame, text="マッピングツール")
        mapping_tool = MappingTool(frame)
        mapping_tool.pack(fill=tk.BOTH, expand=True)

# circus_support_tool.py から呼び出すとき
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Circus Mapping Tool")
    root.geometry("900x600")

    notebook = ttk.Notebook(root)
    notebook.pack(expand=True, fill='both')

    MappingTool.add_to_tab(notebook)  # タブ追加

    root.mainloop()
