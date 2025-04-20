# circusDB_viewer_edit.py

import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import os
import csv
import tkinter.font as tkFont
from tkinter import filedialog
import mapping_module  # mapping_module をインポート

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

# データファイルのパス
CIRCUS_DB_FILE = "circus_db.csv"

class CircusDB_viewer_edit(tk.Frame):  # クラス名が CircusDB_viewer_edit であることを確認
    def __init__(self, parent):
        super().__init__(parent)  # Frame の初期化
        
        # 親フレームに自身を配置 - 適切な配置オプションを使用
        self.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)
        
        # pack_propagateをFalseに設定して、親フレームのサイズに影響されないようにする
        self.pack_propagate(False)

        # circus_db.csv を読み込む
        try:
            self.df = pd.read_csv("circus_db.csv", encoding="utf-8-sig")
        except FileNotFoundError:
            self.df = pd.DataFrame(columns=[
                # ... (既存の columns) ...
            ])

        self.field_sizes = {
            "求人タイトル": {"width": 60, "height": 2},
            "募集予定人数": {"width": 20, "height": 2},
            "仕事内容": {"width": 80, "height": 20},
            "PRポイント": {"width": 80, "height": 5},
            "勤務地住所": {"width": 80, "height": 3},
            "勤務時間補足": {"width": 80, "height": 3},
            "年収例": {"width": 60, "height": 2},
            "給与条件補足": {"width": 80, "height": 3},
            "休日休暇補足": {"width": 80, "height": 3},
            "福利厚生・諸手当": {"width": 80, "height": 5},
            "応募時必須条件": {"width": 80, "height": 5},
            "成果報酬金額": {"width": 40, "height": 2},
            "支払いサイト": {"width": 40, "height": 2},
            "返戻金規定": {"width": 80, "height": 3},
        }

        # メインフレーム（スクロール対応）
        # parentではなく自身(self)の子としてmain_frameを作成
        main_frame = tk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)

        canvas = tk.Canvas(main_frame)
        scrollbar = tk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # 検索エリア
        search_frame = tk.Frame(scrollable_frame) # scrollable_frameに変更
        search_frame.pack(fill=tk.X, pady=5)

        # 企業名入力部分
        company_names = load_company_names()
        tk.Label(search_frame, text="企業名:").grid(row=0, column=0, padx=5)  # ラベルをsearch_frameに配置
        self.company_entry = ttk.Combobox(search_frame, values=company_names, width=40)
        self.company_entry.grid(row=0, column=1, padx=5)  # entryをsearch_frameに配置
        self.company_entry['values'] = [''] + company_names
        self.company_entry.set("")
        self.company_entry.bind("<<ComboboxSelected>>", self.update_management_numbers)

        # 管理番号入力部分
        tk.Label(search_frame, text="管理番号:").grid(row=0, column=2, padx=5)  # ラベルをsearch_frameに配置
        self.management_number_entry = ttk.Combobox(search_frame, values=[], width=15)
        self.management_number_entry.grid(row=0, column=3, padx=5)  # entryをsearch_frameに配置

        # 検索ボタン
        search_button = tk.Button(search_frame, text="検索", command=self.search_record)
        search_button.grid(row=0, column=4, padx=5)  # ボタンをsearch_frameに配置

        # データ表示エリア（ブロック別）
        self.blocks = {
            "募集概要": ["求人タイトル", "募集予定人数", "仕事内容", "PRポイント"],
            "勤務地・勤務時間": ["勤務地住所", "勤務時間補足"],
            "給与・賞与": ["年収例", "給与条件補足"],
            "休日・休暇": ["休日休暇補足"],
            "福利厚生・諸手当": ["福利厚生・諸手当"],
            "求める人材": ["応募時必須条件"],
            "手数料設定": ["成果報酬金額", "支払いサイト", "返戻金規定"],
        }
        self.entries = {}

        # _資料エリアに対応するテキストボックスを直接指定
        self.material_fields = [
            "募集概要_資料", "勤務地・勤務時間_資料", "給与・賞与_資料",
            "休日・休暇_資料", "福利厚生・諸手当_資料", "求める人材_資料",
            "手数料設定_資料"
        ]

        for block, fields in self.blocks.items():
            block_frame = tk.LabelFrame(scrollable_frame, text=block, font=("Arial", 12, "bold"), padx=5, pady=5, relief=tk.GROOVE, borderwidth=2)
            block_frame.pack(fill=tk.X, pady=5)

            content_frame = tk.Frame(block_frame)
            content_frame.pack(fill=tk.X, pady=5)

            left_frame = tk.Frame(content_frame)
            left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

            right_frame = tk.Frame(content_frame, relief=tk.SUNKEN, borderwidth=2)
            right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)

            # _資料エリアのテキストボックスを作成
            for material_field in self.material_fields:
                if material_field.startswith(block):  # material_field が block で始まるかを確認
                    # circus_db.csv からプレースホルダーの値を読み込み
                    placeholder_value = self.df.loc[0, material_field] if not self.df.empty and material_field in self.df.columns else ""

                    # テキストボックスを作成し、プレースホルダーの値を設定
                    text_scrollbar = tk.Scrollbar(right_frame, orient="vertical")  # スクロールバーを作成
                    text_area = tk.Text(right_frame, height=10, width=50, wrap="word",
                                      yscrollcommand=text_scrollbar.set,  # スクロールバーと連携
                                      font=("メイリオ", 9), borderwidth=10, relief="flat", background="white")
                    text_area.insert("1.0", placeholder_value)  # 初期値を設定

                    # entries ディクショナリにテキストボックスを追加
                    self.entries[material_field] = text_area

                    # スクロールバーとテキストボックスを連携させる
                    text_scrollbar.config(command=text_area.yview)

                    # スクロールバーを配置する
                    text_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

                    # テキストボックスを配置する
                    text_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
                    break  # material_field が見つかったらループを抜ける

            # fields をループ処理
            for i, field in enumerate(fields):
                # 項目名ラベルをpackで配置
                label = tk.Label(left_frame, text=field, anchor="w", width=30)
                label.pack(side=tk.TOP, anchor="w", padx=5, pady=5)  # packで配置

                # ラッパーウィジェット (Frame) を作成
                text_frame = tk.Frame(left_frame, borderwidth=10, relief="flat", background="white")  # 枠線設定をFrameに移動
                text_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)  # packで配置

                # スクロールバーを text_frame の子にする
                text_scrollbar_field = tk.Scrollbar(text_frame, orient="vertical")
                text_scrollbar_field.pack(side=tk.RIGHT, fill=tk.Y)  # packで配置

                # entry を作成
                size = self.field_sizes[field]  # self.field_sizes から size を取得

                # フォントサイズを考慮した幅を計算
                font = ("メイリオ", 9)  # 使用するフォント
                font_width = tk.font.Font(font=font).measure("W")  # フォントの幅を取得 (W は平均的な幅の文字)
                width_in_pixels = int(size["width"] * font_width)  # 幅をピクセルに変換

                # width_in_pixels を width プロパティに設定 (修正)
                entry = tk.Text(text_frame, width=size["width"], height=size["height"], wrap="word",
                                yscrollcommand=text_scrollbar_field.set,
                                borderwidth=0, relief="flat", background="white")
                entry.config(font=font)  # font オプションを設定
                entry.pack(side=tk.LEFT, fill=tk.X, expand=True)  # packで配置

                # entry の初期値を circus_db.csv から取得 (サーカスID以外)
                if field != "サーカスID":
                    initial_value = self.df.loc[0, field] if not self.df.empty and field in self.df.columns else ""  # index 0 を仮定、カラムの存在を確認
                    entry.insert("1.0", initial_value)  # entry に初期値を設定

                # スクロールバーとテキストボックスを連携
                text_scrollbar_field.config(command=entry.yview)

                self.entries[field] = entry  # self.entries に entry を追加

        # 入力区分（チェックボタン）
        input_status_frame = tk.Frame(scrollable_frame)
        input_status_frame.pack(fill=tk.X, pady=5)
        tk.Label(input_status_frame, text="入力状態:").pack(side=tk.LEFT, padx=5)
        self.input_status_vars = {
            "未入力": tk.IntVar(),
            "入力済": tk.IntVar(),
            "要更新": tk.IntVar()
        }
        for status, var in self.input_status_vars.items():
            tk.Checkbutton(input_status_frame, text=status, variable=var).pack(side=tk.LEFT)

        # Circus URL 表示欄
        url_frame = tk.Frame(scrollable_frame)
        url_frame.pack(fill=tk.X, pady=5)
        tk.Label(url_frame, text="Circus URL:").pack(side=tk.LEFT, padx=5)
        self.circus_url_entry = tk.Entry(url_frame, width=80)
        self.circus_url_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        # 関連URL 表示欄
        related_url_frame = tk.Frame(scrollable_frame)
        related_url_frame.pack(fill=tk.X, pady=5)
        tk.Label(related_url_frame, text="関連URL:").pack(side=tk.LEFT, padx=5)
        entry_related_url = tk.Entry(related_url_frame, width=80)
        entry_related_url.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        self.entries["関連URL"] = entry_related_url

        # 関連HP 表示欄
        related_hp_frame = tk.Frame(scrollable_frame)
        related_hp_frame.pack(fill=tk.X, pady=5)
        tk.Label(related_hp_frame, text="関連HP:").pack(side=tk.LEFT, padx=5)
        entry_related_hp = tk.Entry(related_hp_frame, width=80)
        entry_related_hp.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        self.entries["関連HP"] = entry_related_hp

        # ボタンエリア
        button_frame = tk.Frame(scrollable_frame)
        button_frame.pack(pady=10)

        tk.Button(button_frame, text="保存", command=self.save_data).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="閉じる", command=self.winfo_toplevel().quit).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="マッピング適用", command=self.apply_mapping_to_circus_db).pack(side=tk.LEFT, padx=5) # マッピング適用ボタンを追加

    def update_record(self):
        # ここに、データを更新する処理を記述します
        # 例えば、circus_db.csv にデータを書き込む処理など
        print("データを更新する処理を実行します")

    def apply_mapping_to_circus_db(self):
        """企業db.csv をマッピングして circus_db.csv に追加する"""
        company_db_path = filedialog.askopenfilename(
            title="企業db.csv を選択",
            filetypes=[("CSV files", "*.csv")]
        )
        if not company_db_path:
            return

        # mapping_module.apply_mapping を呼び出す
        mapping_module.apply_mapping(company_db_path, "circus_db.csv", "circus_db_mapping.csv")

        messagebox.showinfo("マッピング完了", "企業db.csv のデータが circus_db.csv にマッピングされました。")


    def update_management_numbers(self, event=None):
        """企業名に基づいて管理番号リストを更新する"""
        selected_company = self.company_entry.get()

        if selected_company:
            try:
                df = pd.read_csv("circus_db.csv", encoding="utf-8-sig")
                management_numbers = df[df["企業名"] == selected_company]["管理番号"].dropna().unique().tolist()
                self.management_number_entry["values"] = management_numbers
                if management_numbers:
                    self.management_number_entry.set(management_numbers[0])  # 初期値を設定
            except FileNotFoundError:
                messagebox.showerror("エラー", "circus_db.csv が見つかりません")
            except Exception as e:
                messagebox.showerror("エラー", f"管理番号の取得中にエラーが発生しました: {e}")
        else:
            self.management_number_entry["values"] = []
            self.management_number_entry.set("")

    def search_record(self):
        # 検索条件を取得
        company_name = self.company_entry.get().strip()
        management_number = self.management_number_entry.get().strip() 

        try:
            # circus_db.csv を読み込む
            df = pd.read_csv("circus_db.csv", encoding="utf-8-sig")

            # 検索条件でデータをフィルタリング
            df = df.fillna("")  # NaN を空文字に変換
            filtered_df = df[
                (df["管理番号"].astype(str) == str(management_number)) &  # 管理番号を str に変換
                (df["企業名"].astype(str).isin([str(company_name)]))  # 企業名を str に変換
            ]

            # 該当するデータがあれば、入力エリアに表示
            if not filtered_df.empty:
                record = filtered_df.iloc[0].to_dict()  # 最初のレコードを取得
                print("record:", record)  # record変数の中身を出力

                # 入力エリアに値を設定
                for field, entry in self.entries.items():
                    # material_fields に含まれるフィールドのみ更新
                    if field in self.material_fields and field in record:
                        entry.delete("1.0", tk.END)  # 既存の内容をクリア
                        entry.insert("1.0", str(record.get(field, "")))  # 新しい値を設定 (文字列に変換)

                    # entry が Text ウィジェットで、かつ record に field が存在する場合のみ更新
                    if isinstance(entry, tk.Text) and field in record:
                        value = record.get(field, "")
                        if isinstance(value, float):  # float型の場合、文字列に変換
                            value = str(value)
                        entry.delete("1.0", tk.END)  # 既存の内容をクリア
                        entry.insert("1.0", value)  # 新しい値を設定 (文字列に変換)
                    elif isinstance(entry, tk.Entry) and field in record:
                        entry.delete(0, tk.END)  # Entryウィジェットの場合の既存内容クリア方法
                        entry.insert(0, str(record.get(field, "")))  # Entryに値を設定

                # 入力状態を設定
                for status, var in self.input_status_vars.items():
                    var.set(1 if status in str(record.get("入力状態", "")) else 0)

                # Circus URL を設定
                self.circus_url_entry.delete(0, tk.END)  # 既存の内容をクリア
                self.circus_url_entry.insert(0, record.get("Circus URL", ""))

            else:
                # 該当データがない場合、新規入力として処理
                messagebox.showinfo("新規入力", "該当するデータがありません。新規入力として処理します。")

                # 新規データを作成
                new_data = {
                    "企業名": company_name,
                    "管理番号": management_number,
                }

                # その他のフィールドに初期値を設定
                for column in df.columns:  # 既存のヘッダーからカラム名を取得
                    if column not in new_data:  # 企業名と管理番号以外は初期値を設定
                        new_data[column] = "（入力待ち）"

                # circus_db.csv に追記
                try:
                    with open("circus_db.csv", "a", encoding="utf-8-sig", newline="") as f:
                        writer = csv.DictWriter(f, fieldnames=df.columns)  # 既存のヘッダーを使用
                        writer.writerow(new_data)  # 新規データを追加
                    messagebox.showinfo("保存完了", "新規データが circus_db.csv に保存されました。")
                except Exception as e:
                    messagebox.showerror("エラー", f"保存中にエラーが発生しました: {e}")

        except FileNotFoundError:
            messagebox.showerror("エラー", "circus_db.csv が見つかりません")
        except Exception as e:
            messagebox.showerror("エラー", f"検索中にエラーが発生しました: {e}")

    def save_data(self):
        # 入力内容を取得
        data = {}
        for field, entry in self.entries.items():
            if isinstance(entry, tk.Text):
                data[field] = entry.get("1.0", tk.END).strip()
            elif isinstance(entry, tk.Entry):
                data[field] = entry.get().strip()

        # 管理番号、入力状態、Circus URL を取得
        data["管理番号"] = self.management_number_entry.get().strip()
        data["入力状態"] = ", ".join([status for status, var in self.input_status_vars.items() if var.get() == 1])
        data["Circus URL"] = self.circus_url_entry.get().strip()
        data["企業名"] = self.company_entry.get().strip()

        # circus_db.csv の既存データを読み込む
        csv_file = "circus_db.csv"
        try:
            if os.path.exists(csv_file):
                self.df = pd.read_csv(csv_file, encoding="utf-8-sig", dtype=str).fillna("")
            else:
                self.df = pd.DataFrame(columns=data.keys())
        except Exception as e:
            messagebox.showerror("エラー", f"CSV 読み込みエラー: {e}")
            return

        # NaN 値を空文字に変換
        for key in ["管理番号", "入力状態", "企業名"]:
            if not isinstance(data.get(key), str) or pd.isna(data[key]):
                data[key] = ""

        # 管理番号をキーにしてデータを更新
        if "管理番号" in self.df.columns and data["管理番号"] in self.df["管理番号"].astype(str).values:
            self.df.loc[self.df["管理番号"].astype(str) == data["管理番号"], data.keys()] = list(data.values())
        else:
            self.df = pd.concat([self.df, pd.DataFrame([data])], ignore_index=True)

        # **データの型を統一 (検索時に一致するようにする)**
        self.df = self.df.astype(str)

        # データを保存
        try:
            self.df.to_csv(csv_file, index=False, encoding="utf-8-sig")
            messagebox.showinfo("保存完了", "データが circus_db.csv に保存されました。")
        except Exception as e:
            messagebox.showerror("エラー", f"保存中にエラーが発生しました: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = CircusDB_viewer_edit(root)
    root.mainloop()
