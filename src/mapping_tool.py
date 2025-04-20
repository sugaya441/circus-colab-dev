import tkinter as tk
from tkinter import messagebox, filedialog
from tkinter import ttk
import pandas as pd
import os
import csv
import datetime
from mapping_cache_controller import MappingCacheController
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(BASE_DIR)
CIRCUS_DB_FILE = os.path.join(BASE_DIR, 'circus_db.csv')
MAPPING_FILE = os.path.join(BASE_DIR, 'circus_db_mapping.csv')
BACKUP_DIR = os.path.join(BASE_DIR, 'backup')
os.makedirs(BACKUP_DIR, exist_ok=True)
df_company = None

def load_company_names(csv_path='企業管理DB.csv'):
    try:
        df = pd.read_csv(csv_path, encoding='utf-8')
        return df['企業名'].dropna().unique().tolist()
    except FileNotFoundError:
        return []
    except Exception as e:
        print(f'企業名読み込みエラー: {e}')
        return []

def load_company_db():
    global df_company
    file_path = filedialog.askopenfilename(filetypes=[('CSV files', '*.csv')])
    if not file_path:
        return
    df_company = pd.read_csv(file_path, encoding='utf-8-sig')
    messagebox.showinfo('成功', '企業DBを読み込みました。')

def get_company_list():
    data_dir = os.path.join(BASE_DIR, 'data')
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    return [f.replace('.csv', '') for f in os.listdir(data_dir) if f.endswith('.csv')]

class MappingTool(tk.Frame):

    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.mapping_cache = {}
        self.next_no = 1
        self.cache_controller = MappingCacheController()
        self.cache_controller.load_from_file()
        self.create_main_window()

    def save_mapping(self):
        company_name = self.company_entry.get()
        management_number = self.management_number_entry.get()
        if not company_name or not management_number:
            messagebox.showerror('エラー', '企業名と管理番号を入力してください。')
            return
        existing_no = None
        for no, row in self.cache_controller.mapping_cache.items():
            if row.get('企業名') == company_name and row.get('管理番号の文字列') == management_number:
                existing_no = no
                break
        if existing_no is not None:
            no = existing_no
            messagebox.showinfo('取得', f'既存のデータを取得しました。（No. {no}）')
        else:
            no = self.next_no
            self.next_no += 1
            self.cache_controller.mapping_cache[no] = {'No.': no, '企業名': company_name, '管理番号の文字列': management_number}
            messagebox.showinfo('保存', f'企業名と管理番号をキャッシュに保存しました。（No. {no}）')

    def save_all(self):
        self.cache_controller.save_to_file()
        messagebox.showinfo('保存完了', 'マッピングルールを保存しました。')

    def create_main_window(self):
        tk.Label(self, text='マッピングツール', font=('Arial', 16)).pack(pady=10)
        top_frame = tk.Frame(self)
        top_frame.pack(fill=tk.X, padx=10, pady=5)
        tk.Button(top_frame, text='企業DBを読み込み', command=load_company_db).pack(side=tk.LEFT, padx=5)
        company_names = load_company_names()
        tk.Label(top_frame, text='企業名を入力:').pack(side=tk.LEFT, pady=5)
        self.company_entry = ttk.Combobox(top_frame, values=company_names, width=40)
        self.company_entry.pack(side=tk.LEFT, padx=5)
        self.company_entry.bind('<<ComboboxSelected>>', self.update_management_number_list)
        tk.Label(top_frame, text='管理番号の文字列:').pack(side=tk.LEFT, padx=5)
        self.management_number_entry = ttk.Combobox(top_frame, values=[], width=15)
        self.management_number_entry.pack(side=tk.LEFT, padx=5)
        self.management_number_entry.set('新規入力可')
        self.management_number_entry.bind('<KeyRelease>', self.allow_custom_management_number)
        tk.Button(top_frame, text='確定', command=self.save_mapping).pack(side=tk.LEFT, padx=5)
        tk.Button(self, text='マッピングルール保存', command=self.save_all).pack(pady=5)
        self.create_blocks()

    def update_management_number_list(self, event=None):
        company_name = self.company_entry.get()
        if not company_name or not os.path.exists(MAPPING_FILE):
            return
        try:
            management_numbers = set()
            with open(MAPPING_FILE, 'r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row['企業名'] == company_name:
                        management_numbers.add(row['管理番号の文字列'])
            self.management_number_entry['values'] = list(management_numbers) + ['新規入力可']
        except Exception as e:
            print(f'管理番号更新エラー: {e}')
            messagebox.showerror('エラー', '管理番号リストの更新中にエラーが発生しました。')

    def allow_custom_management_number(self, event=None):
        self.management_number_entry.set(self.management_number_entry.get())

    def get_current_no(self):
        company_name = self.company_entry.get()
        management_number = self.management_number_entry.get()
        for existing_no, data in self.cache_controller.mapping_cache.items():
            if data.get('企業名') == company_name and data.get('管理番号の文字列') == management_number:
                return existing_no
        return None

    def create_blocks(self):
        blocks = {'募集概要': ['求人タイトル', '募集予定人数', '仕事内容', 'PRポイント', '募集概要_資料'], '勤務地・勤務時間': ['勤務地住所', '勤務時間補足', '勤務地・勤務時間_資料'], '給与・賞与': ['年収例', '給与条件補足', '給与・賞与_資料'], '休日・休暇': ['休日休暇補足', '休日・休暇_資料'], '福利厚生・諸手当': ['福利厚生・諸手当', '福利厚生・諸手当_資料'], '求める人材': ['応募時必須条件', '求める人材_資料'], '手数料設定': ['成果報酬金額', '支払いサイト', '返戻金規定', '手数料設定_資料']}
        main_frame = tk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        for i, (block, fields) in enumerate(blocks.items()):
            frame = tk.LabelFrame(main_frame, text=block, padx=5, pady=5)
            frame.grid(row=i // 3, column=i % 3, padx=5, pady=5, sticky='nsew')
            for col in fields:
                tk.Button(frame, text=f'{col} を編集', command=lambda c=col: self.open_window_editor(c, self.get_current_no())).pack(pady=2)

    def open_window_editor(self, column_name, no=None):
        if no is None:
            no = self.get_current_no()
        if no is None:
            messagebox.showerror('エラー', '企業名と管理番号が未入力、または正しく確定されていません。')
            return
        if no not in self.cache_controller.mapping_cache:
            self.cache_controller.mapping_cache[no] = {}
        edit_window = tk.Toplevel()
        edit_window.title(f'{column_name} - 文面作成 / 編集')
        edit_window.geometry('700x500')
        tk.Label(edit_window, text='プレビュー:').pack(pady=5)
        preview_text = tk.Text(edit_window, height=8, wrap='word')
        preview_text.pack(padx=10, pady=5, expand=True, fill='both')
        tk.Label(edit_window, text='文面編集:').pack(pady=5)
        edit_text = tk.Text(edit_window, height=10, wrap='word')
        existing_text = self.cache_controller.mapping_cache[no].get(column_name, '')
        edit_text.insert('1.0', existing_text)
        edit_text.pack(padx=10, pady=5, expand=True, fill='both')
        self.update_preview(edit_text, preview_text)
        edit_text.bind('<KeyRelease>', lambda event: self.update_preview(edit_text, preview_text))
        dropdown_frame = tk.Frame(edit_window)
        dropdown_frame.pack(pady=10)
        tk.Label(dropdown_frame, text='挿入する企業DB項目').grid(row=0, column=0, padx=5)
        column_list = list(df_company.columns) if df_company is not None else []
        item_name_selector = ttk.Combobox(dropdown_frame, values=column_list, width=30)
        item_name_selector.grid(row=0, column=1, padx=5)

        def insert_item_name():
            item_name = item_name_selector.get()
            if item_name:
                edit_text.insert(tk.INSERT, f'{{{item_name}}}')
                self.update_preview(edit_text, preview_text)
        tk.Button(dropdown_frame, text='項目を挿入', command=insert_item_name).grid(row=1, column=1, padx=5)
        tk.Button(edit_window, text='保存', command=lambda: self.save_changes(column_name, edit_text, preview_text, edit_window)).pack(pady=10)

    def update_preview(self, edit_text, preview_text):
        try:
            if df_company is not None and (not df_company.empty):
                test_data = df_company.iloc[0].to_dict()
            else:
                test_data = {}
            raw_text = edit_text.get('1.0', tk.END).strip()
            formatted_text = raw_text.format(**test_data)
            preview_text.delete('1.0', tk.END)
            preview_text.insert('1.0', formatted_text if formatted_text else 'データがありません。')
        except KeyError as e:
            preview_text.delete('1.0', tk.END)
            preview_text.insert('1.0', f'プレビューの更新中にキーエラーが発生しました: {e}')
        except Exception as e:
            preview_text.delete('1.0', tk.END)
            preview_text.insert('1.0', 'プレビューの更新中にエラーが発生しました。')

    def save_changes(self, column_name, edit_text, preview_text, edit_window):
        correct_no = self.get_current_no()
        if correct_no is None:
            messagebox.showerror('エラー', '企業名と管理番号を確定してください。')
            return
        if correct_no not in self.cache_controller.mapping_cache:
            self.cache_controller.mapping_cache[correct_no] = {}
        new_text = edit_text.get('1.0', tk.END).strip()
        self.cache_controller.mapping_cache[correct_no][column_name] = new_text
        messagebox.showinfo('保存完了', f'{column_name} の内容をキャッシュに保存しました。（No. {correct_no}）')
        self.update_preview(edit_text, preview_text)
        edit_window.destroy()

    @staticmethod
    def add_to_tab(parent_notebook):
        frame = ttk.Frame(parent_notebook)
        parent_notebook.add(frame, text='マッピングツール')
        mapping_tool = MappingTool(frame)
        mapping_tool.pack(fill=tk.BOTH, expand=True)
if __name__ == '__main__':
    root = tk.Tk()
    root.title('Circus Mapping Tool')
    root.geometry('900x600')
    notebook = ttk.Notebook(root)
    notebook.pack(expand=True, fill='both')
    MappingTool.add_to_tab(notebook)
    root.mainloop()