##kigyouDB.py

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import json
import os
import pandas as pd
import csv
import re
import pandas as pd

def load_company_names(csv_path="企業管理DB.csv"): # インデントを修正
    """企業管理DB.csvから企業名を読み込み、リストとして返す"""
    try:
        df = pd.read_csv(csv_path, encoding="utf-8")
        company_names = df["企業名"].dropna().unique().tolist()  # 企業名カラムから重複を除いてリスト化
        return company_names
    except FileNotFoundError:
        print(f"Error: '{csv_path}'が見つかりません。")
        return []
    except Exception as e:
        print(f"Error: 企業名を読み込み中にエラーが発生しました: {e}")
        return []

def get_company_info(company_name, csv_path="企業管理DB.csv"):
    """企業管理DB.csv から指定された企業名の情報を取得"""
    try:
        df = pd.read_csv(csv_path, encoding="utf-8")
        
        matching_rows = df[df["企業名"].str.strip() == company_name.strip()]
        
        if matching_rows.empty:
            print(f"Warning: 企業名 '{company_name}' が見つかりません。デフォルト値を使用します。")
            return "無", "X", "標準", 1  # デフォルト値を返す

        company_data = matching_rows.iloc[0]

        derivative_type = str(company_data.get("派生タイプ", "無")).strip()
        identification_alphabet = str(company_data.get("識別アルファベット", "X")).strip()
        number_generation_type = str(company_data.get("番号生成タイプ", "標準")).strip()

        if "派生数" in company_data and derivative_type == "有":
            derivative_count = int(company_data["派生数"])
        else:
            derivative_count = 1

        print(f"[DEBUG] 企業名: {company_name}, 派生タイプ: {derivative_type}, 識別アルファベット: {identification_alphabet}, 番号生成タイプ: {number_generation_type}, 派生数: {derivative_count}")
        return derivative_type, identification_alphabet, number_generation_type, derivative_count

    except Exception as e:
        print(f"Error: 企業情報の取得中にエラーが発生しました: {e}")
        return "無", "X", "標準", 1  # デフォルト値を返す



# データ保存ディレクトリ
DATA_DIR = "data/"
os.makedirs(DATA_DIR, exist_ok=True)

# 日本の都道府県リスト
PREFECTURES = [
    "北海道", "青森県", "岩手県", "宮城県", "秋田県", "山形県", "福島県",
    "茨城県", "栃木県", "群馬県", "埼玉県", "千葉県", "東京都", "神奈川県",
    "新潟県", "富山県", "石川県", "福井県", "山梨県", "長野県", "岐阜県",
    "静岡県", "愛知県", "三重県", "滋賀県", "京都府", "大阪府", "兵庫県",
    "奈良県", "和歌山県", "鳥取県", "島根県", "岡山県", "広島県", "山口県",
    "徳島県", "香川県", "愛媛県", "高知県", "福岡県", "佐賀県", "長崎県",
    "熊本県", "大分県", "宮崎県", "鹿児島県", "沖縄県"
]

# 企業ごとのデータファイルを取得
def get_company_db_file(company_name):
    return os.path.join(DATA_DIR, f"{company_name}_db.csv")

def select_location_column(headers):
    """
    「勤務地住所」に該当するカラムをユーザーに選択させるウィンドウ
    """
    root = tk.Toplevel()
    root.title("勤務地カラム選択")
    root.geometry("400x200")

    tk.Label(root, text="勤務地を取得するカラムを選択してください:").pack(pady=5)

    # 「勤務地」「住所」「派遣先」を含む候補を抽出
    candidates = [col for col in headers if "勤務地" in col or "住所" in col or "派遣先" in col]
    if not candidates:
        candidates = headers  # 何も該当しない場合はすべてのカラムを候補にする

    selected_col = tk.StringVar(value=candidates[0])  # 初期値

    dropdown = ttk.Combobox(root, textvariable=selected_col, values=candidates, state="readonly")
    dropdown.pack(pady=5)

    def confirm_selection():
        """
        ユーザーがカラムを選択した際に実行
        """
        root.result = selected_col.get()  # root.result に選択値を格納
        print(f"選択された勤務地カラム: {root.result}")  # デバッグ用
        root.destroy()

    tk.Button(root, text="確定", command=confirm_selection).pack(pady=10)

    root.result = None
    root.wait_window()  # ユーザーの選択を待つ
    return root.result

def extract_city_municipality(address):
    """
    住所から都道府県+市町村部分を抽出
    """
    if not address:
        return ""

    for pref in PREFECTURES:
        if address.startswith(pref):
            remaining = address[len(pref):].strip()
            match = re.search(r"^(市|区|町|村)[^、\s]+", remaining)
            if match:
                return f"{pref}{match.group()}"
            return pref  # 市町村が見つからない場合、都道府県のみ
    return ""

def enhanced_extract_city_municipality(address):
    """
    住所から都道府県+市町村部分を抽出（補完ロジックを強化）
    """
    if not address:
        return "不明"

    for pref in PREFECTURES:
        if address.startswith(pref):
            remaining = address[len(pref):].strip()
            match = re.search(r"(.+?[市区町村])", remaining)
            if match:
                return f"{pref} {match.group(1)}"
            alt_match = re.search(r"(.+?郡.+?[町村])", remaining)
            if alt_match:
                return f"{pref} {alt_match.group()}"
            
            cleaned_remaining = re.split(r"[丁目番地]", remaining)[0]
            last_attempt = re.search(r"(.+?[市区町村])", cleaned_remaining)
            if last_attempt:
                return f"{pref} {last_attempt.group()}"
            
            return f"{pref} 不明"
    return "不明"

    # 改行コードを削除
    city_municipality = city_municipality.replace('\n', '').replace('\r', '')

    return city_municipality

def clean_pasted_data(pasted_data, headers):
    """
    データの前処理（タブ区切りのデータを整形）
    """
    cleaned_data = []
    rows = pasted_data.strip().split("\n")
    temp_row = ""

    for row in rows:
        if row.strip().startswith("\\"):  # 行頭が \ で始まるかチェック
            if temp_row:
                cleaned_data.append(temp_row.strip().split("\t"))
            temp_row = row[1:].strip()  # \ を除いて temp_row に追加
        else:
            temp_row += " " + row.strip()  # \ がない場合はそのまま追加

    if temp_row:
        cleaned_data.append(temp_row.strip().split("\t"))

    corrected_data = []
    expected_length = len(headers)  # **想定するカラム数**

    for cells in cleaned_data:
        # **デバッグ: 各行のデータを確認**
        print(f"デバッグ: クリーニング後のデータ = {cells}, 期待するカラム数 = {expected_length}, 実際のカラム数 = {len(cells)}")

        if len(cells) < expected_length:
            # **不足している場合、空のデータを追加**
            missing_count = expected_length - len(cells)
            cells += [""] * missing_count
            print(f"⚠️ カラム数不足: {missing_count} 個の空データを追加 → {cells}")
        elif len(cells) > expected_length:
            # **余分なデータがある場合、カット**
            print(f"⚠️ カラム数過剰: {len(cells) - expected_length} 個のデータをカット")
            cells = cells[:expected_length]

        corrected_data.append(cells)

    return corrected_data[1:]  # **最初の行(ヘッダー)をデータとして認識しない**

def confirm_and_preview_data(data_list, headers, company_name):
    """
    データ確認用プレビューウィンドウ
    """

    # **「勤務地住所」カラムをユーザーに選択させる**
    location_column = select_location_column(headers)
    if not location_column:
        messagebox.showerror("エラー", "勤務地住所のカラムが選択されませんでした。")
        return

    print(f"[DEBUG] 選択された勤務地カラム: {location_column}")  # デバッグ用

    # **「勤務地市町村」データを抽出**
    for row in data_list:
        if location_column in row and row[location_column].strip():
            extracted_city = enhanced_extract_city_municipality(row[location_column])
            row["勤務地市町村"] = extracted_city
            print(f"[DEBUG] 住所: {row[location_column]} → 抽出された市町村: {extracted_city}")  # デバッグ用
        else:
            row["勤務地市町村"] = "不明"

    # **「管理番号」を最初、「勤務地市町村」を最後に配置**
    if "勤務地市町村" not in headers:
        headers.append("勤務地市町村")

    headers = ["管理番号"] + [h for h in headers if h not in ["管理番号", "勤務地市町村"]] + ["勤務地市町村"]

    confirm_window = tk.Toplevel()
    confirm_window.title("データ確認")
    confirm_window.geometry("900x600")

    # **フレーム作成**
    tree_frame = tk.Frame(confirm_window, width=800, height=500)  
    tree_frame.pack(fill=tk.BOTH, expand=True)
    tree_frame.pack_propagate(0)  # 自動調整を無効化

    # **Treeview 作成**
    tree = ttk.Treeview(tree_frame, columns=headers, show="headings", height=20)

    # **カラムヘッダー設定**
    for header in headers:
        tree.heading(header, text=header)
        tree.column(header, width=120 if header in ["管理番号", "勤務地市町村"] else 100, anchor="center")

    # **データ挿入**
    for row_index, row_data in enumerate(data_list):
        values = [row_data.get(header, "") for header in headers]  
        tree.insert("", tk.END, values=values, iid=row_index)  

    tree.pack()

    # **スクロールバー追加**
    scrollbar_y = tk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
    scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)

    scrollbar_x = tk.Scrollbar(confirm_window, orient="horizontal", command=tree.xview)
    scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)

    tree.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)

    # **保存処理**
    def save_data():
        file_name = get_company_db_file(company_name)
        save_to_csv(file_name, data_list, headers)
        confirm_window.destroy()

    # **ボタン配置**
    tk.Button(confirm_window, text="保存", command=save_data).pack(pady=10)
    tk.Button(confirm_window, text="閉じる", command=confirm_window.destroy).pack(pady=10)
    
def save_to_csv(file_name, data_list, headers):
    """
    データを CSV に保存
    """
    # ヘッダーに "勤務地市町村" が含まれていない場合に追加
    if "勤務地市町村" not in headers:
        headers.append("勤務地市町村")

    # ... (CSV ファイルへの保存処理は省略) ...
    try:
        with open(file_name, mode="w", encoding="utf-8-sig", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=headers)
            writer.writeheader()
            writer.writerows(data_list)
        messagebox.showinfo("保存完了", f"データが {file_name} に保存されました。")
    except Exception as e:
        messagebox.showerror("エラー", f"保存中にエラーが発生しました: {e}")

# メインGUI
class KigyouDBManager(tk.Frame):
    def __init__(self, master=None):
        if master is None:
            master = tk.Tk()  # masterがNoneの場合、Tkウィンドウを作成
        super().__init__(master)
        self.master = master
        self.pack(fill=tk.BOTH, expand=True)

        # 例外ハンドラーを設定
        self.master.report_callback_exception = self.custom_exception_handler

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(expand=True, fill='both')

        self.create_main_tab()
        self.create_paste_tab()

        self.company_name = ""  # company_name を初期化

    def custom_exception_handler(self, exc, val, tb):
        messagebox.showerror("エラー", f"予期しないエラーが発生しました:\n{val}")

    def create_main_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="メイン")

        # load_company_names 関数を使用して企業名リストを取得
        company_names = load_company_names()
        tk.Label(tab, text="企業名を入力:").pack(pady=5)
        self.company_entry = ttk.Combobox(tab, values=company_names, width=40)  # Comboboxに変更
        self.company_entry.pack(pady=5)

        tk.Button(tab, text="データペーストして確認", command=self.switch_to_paste_tab).pack(pady=10)


    def create_paste_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="データペースト")

        tk.Label(tab, text="企業DBのデータをペーストしてください:").pack(pady=5)
        self.text_box = tk.Text(tab, height=10, width=70)
        self.text_box.pack(pady=5)

        tk.Button(tab, text="確定", command=self.process_paste).pack(pady=10)

    def switch_to_paste_tab(self):
        self.notebook.select(1)
        # company_name を取得する処理をここに移動
        self.company_name = self.company_entry.get().strip()


    def process_paste(self):
        """ペーストデータを処理（①通常・②その他（派生あり）・③その他（派生なし））"""
        pasted_text = self.text_box.get("1.0", tk.END).strip()
        headers = pasted_text.split("\n")[0].split("\t")

        # **データの前処理**
        cleaned_data = clean_pasted_data(pasted_text, headers)
        original_data_list = [dict(zip(headers, row)) for row in cleaned_data]

        # **企業情報（派生情報 + 番号生成タイプ）を取得**
        derivative_type, identification_alphabet, number_generation_type, derivative_count = get_company_info(self.company_name)

        print(f"[DEBUG] 番号生成タイプ: {number_generation_type}, 派生数: {derivative_count}")  # デバッグ用

        if derivative_type == "無" and identification_alphabet == "X":
            print(f"Warning: 企業 '{self.company_name}' の情報が見つからず、デフォルト値を使用します。")

        # **③その他（派生なし）のケースのみプレースホルダー選択を表示**
        if number_generation_type.strip() == "その他" and derivative_type == "無":
            print("[DEBUG] 番号生成タイプが 'その他' かつ 派生なしのため、項目選択ダイアログを表示")
            self.prompt_placeholder_selection(original_data_list, headers, identification_alphabet)
        else:
            print("[DEBUG] ①通常 or ②その他（派生あり）の番号生成を実行")
            self.generate_management_numbers(original_data_list, headers, identification_alphabet, derivative_type, derivative_count)

    def prompt_placeholder_selection(self, data_list, headers, identification_alphabet):
        """プレースホルダーを選択するダイアログを表示（③その他の処理）"""
        self.placeholder_window = tk.Toplevel(self.master)
        self.placeholder_window.title("管理番号のプレースホルダー選択")
        self.placeholder_window.geometry("400x200")

        tk.Label(self.placeholder_window, text="管理番号を作成するために使用する項目を選択してください:").pack()

        selected_var = tk.StringVar(self.placeholder_window)
        if headers:
            selected_var.set(headers[0])  # **デフォルト選択**
        else:
            selected_var.set("")  # **空の値でエラー防止**

        dropdown = ttk.Combobox(self.placeholder_window, textvariable=selected_var, values=headers, state="readonly")
        dropdown.pack()

        def on_confirm():
            selected_placeholder = selected_var.get()
            print(f"[DEBUG] 選択されたプレースホルダー: {selected_placeholder}")  # デバッグ用
            self.placeholder_window.destroy()
            self.generate_management_numbers(data_list, headers, identification_alphabet, "無", 1, selected_placeholder)

        confirm_button = tk.Button(self.placeholder_window, text="確定", command=on_confirm)
        confirm_button.pack()

        # **エラー防止: ウィンドウが閉じられる前に `wait_window()` を使う**
        self.placeholder_window.result = None
        self.placeholder_window.wait_window()  # ユーザーの選択を待つ

    def generate_management_numbers(self, data_list, headers, identification_alphabet, derivative_type, derivative_count, placeholder_column=None):
        """管理番号を ①通常, ②その他（派生あり）, ③その他（派生なし） の形式で生成"""
        new_data_list = []
        base_number_counter = 1  # **連番カウンター**

        for row in data_list:
            # **③その他（派生なし）の場合はプレースホルダーを使用**
            placeholder_value = row.get(placeholder_column, "") if placeholder_column and derivative_type == "無" else ""

            # **連番をゼロ埋めしない**
            base_number = str(base_number_counter)
            base_number_counter += 1  # 次の番号へ

            # **①通常（派生なし） の場合**
            if derivative_type == "無" and not placeholder_column:
                management_number = f"{identification_alphabet}{base_number}"
                new_row = row.copy()
                new_row["管理番号"] = management_number
                new_data_list.append(new_row)

            # **②その他（派生あり） の場合**
            elif derivative_type == "有":
                for i in range(1, derivative_count + 1):
                    new_row = row.copy()
                    management_number = f"{identification_alphabet}{base_number}派生{i}"  # 「P」→「派生」に修正
                    new_row["管理番号"] = management_number
                    new_data_list.append(new_row)

            # **③その他（派生なし） の場合**
            elif derivative_type == "無" and placeholder_column:
                management_number = f"{identification_alphabet}{base_number}{placeholder_value}"
                new_row = row.copy()
                new_row["管理番号"] = management_number
                new_data_list.append(new_row)

        print(f"[DEBUG] 生成された管理番号リスト: {[row['管理番号'] for row in new_data_list]}")  # デバッグ用
        confirm_and_preview_data(new_data_list, headers, self.company_name)

if __name__ == "__main__":
    app = KigyouDBManager()
    app.mainloop()
