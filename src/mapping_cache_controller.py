from data_saver import save_to_file
import csv
from collections import OrderedDict

class MappingCacheController:

    def __init__(self):
        self.mapping_cache = OrderedDict()
        self.next_no = 1
        self.mapping_file_path = 'circus_db_mapping.csv'

    def load_from_file(self, path=None):
        path = path or self.mapping_file_path
        self.mapping_cache.clear()
        try:
            with open(path, newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    no = int(row.get('No.', self.next_no))
                    self.mapping_cache[no] = row
                    self.next_no = max(self.next_no, no + 1)
        except FileNotFoundError:
            pass

    def save_to_file(self):
        save_to_file(self.mapping_cache)

    def upsert_entry(self, company_name, management_number, data_dict):
        for no, row in self.mapping_cache.items():
            if row.get('企業名') == company_name and row.get('管理番号') == management_number:
                self.mapping_cache[no] = data_dict
                return no
        new_no = self.next_no
        self.mapping_cache[new_no] = data_dict
        self.next_no += 1
        return new_no

    def get_by_company_and_number(self, company_name, management_number):
        for row in self.mapping_cache.values():
            if row.get('企業名') == company_name and row.get('管理番号') == management_number:
                return row
        return None

    def get_all(self):
        return list(self.mapping_cache.values())