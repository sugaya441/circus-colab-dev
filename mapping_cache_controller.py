# === このファイルの責務（GPT用構造補助） ===
# mapping_cache_controller.py：
# 本ファイルは「編集中のマッピングルールキャッシュ操作（取得・追加・更新）」を担う
# 保存処理は data_saver.py に委譲される

import csv
from collections import OrderedDict

class MappingCacheController:
    def __init__(self):
        self.mapping_cache = OrderedDict()
        self.next_no = 1
        self.mapping_file_path = "circus_db_mapping.csv"

    def load_from_file(self, path=None):
        path = path or self.mapping_file_path
        self.mapping_cache.clear()
        try:
            with open(path, newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    no = int(row.get("No.", self.next_no))
                    self.mapping_cache[no] = row
                    self.next_no = max(self.next_no, no + 1)
        except FileNotFoundError:
            pass  # 初回はファイルが存在しない場合があるため無視

    
    def save_to_file(self, path=None):
        import os
        from data_saver import load_circus_db, save_circus_db

        path = path or self.mapping_file_path

        if os.path.exists(path):
            existing_data = load_circus_db(path)
        else:
            existing_data = {}

        # 編集されたキーのみ上書き
        for no, row in self.mapping_cache.items():
            existing_data[no] = row

        # 保存
        save_circus_db(existing_data, path)

    def upsert_entry(self, company_name, management_number, data_dict):
        for no, row in self.mapping_cache.items():
            if row.get("企業名") == company_name and row.get("管理番号") == management_number:
                self.mapping_cache[no] = data_dict
                return no
        new_no = self.next_no
        self.mapping_cache[new_no] = data_dict
        self.next_no += 1
        return new_no

    def get_by_company_and_number(self, company_name, management_number):
        for row in self.mapping_cache.values():
            if row.get("企業名") == company_name and row.get("管理番号") == management_number:
                return row
        return None

    def get_all(self):
        return list(self.mapping_cache.values())
