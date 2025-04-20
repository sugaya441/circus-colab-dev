import pandas as pd
import os
import csv
from tkinter import messagebox

class MappingError(Exception):
    """マッピング処理中に発生するエラー"""
    pass

def validate_rule(rule, company_columns):
    """ルールが正しく適用できるかを検証する"""
    for circus_col, company_col_template in rule.items():
        if company_col_template:
            try:
                company_col_template.format(**{col: "" for col in company_columns})
            except KeyError as e:
                raise MappingError(f"ルール '{circus_col}' に無効な企業dbカラム '{e}' が含まれています。") from e
            except ValueError as e:
                raise MappingError(f"ルール '{circus_col}' の形式が正しくありません: {e}") from e

def apply_rule(company_row, rule, for_preview=False):
    """ルールを適用して新しいCircusDBのデータ行を生成する"""
    new_circus_row = {}
    for circus_col, company_col_template in rule.items():
        if company_col_template:
            try:
                new_circus_row[circus_col] = company_col_template.format(**company_row)
            except KeyError as e:
                if for_preview:
                    new_circus_row[circus_col] = ""
                else:
                    raise MappingError(f"企業db.csv に '{e.args[0]}' カラムが存在しません。") from e  # KeyErrorが発生した場合、エラーメッセージにカラム名を含める
            
        else:
            new_circus_row[circus_col] = ""
    return new_circus_row

def load_mapping_rules(mapping_path, company_name, management_number):
    """マッピングルールを読み込む"""
    mapping_rules = []
    try:
        with open(mapping_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['企業名'] == company_name and row['管理番号の文字列'] == management_number:
                    mapping_rules.append({
                        col: row[col] for col in reader.fieldnames if col not in ["No.", "企業名", "管理番号の文字列"]
                    })
    except FileNotFoundError as e:
        raise MappingError(f"マッピングルールファイルが見つかりません: {e}") from e  # MappingErrorでラップして再送出
    except Exception as e:
        raise MappingError(f"マッピングルールの読み込み中にエラーが発生しました: {e}") from e  # MappingErrorでラップして再送出
    return mapping_rules

def execute_mapping(company_name, management_number, rule, company_db_path):
    """マッピング処理を実行"""
    try:
        df_company = pd.read_csv(company_db_path, encoding="utf-8-sig")
        validate_rule(rule, df_company.columns) 

        df_circus = pd.read_csv("circus_db.csv", encoding="utf-8-sig")
        processed_count = 0

        for _, company_row in df_company.iterrows():
            if management_number in str(company_row['管理番号']):
                new_circus_row = apply_rule(company_row, rule)
                new_circus_row['企業名'] = company_name
                new_circus_row['管理番号'] = company_row['管理番号']
                df_circus = pd.concat([df_circus, pd.DataFrame([new_circus_row])], ignore_index=True)
                processed_count += 1

        df_circus.to_csv("circus_db.csv", index=False, encoding="utf-8-sig")
        print(f"{processed_count} 件のデータをマッピングしました。")  

    except (FileNotFoundError, ValueError, KeyError) as e:
        raise MappingError(f"マッピング中にエラーが発生しました: {e}") from e  # MappingErrorでラップして再送出


def execute_mapping_with_rules(company_name, management_number, rules, company_db_path, selected_tab_index=0):
    """選択されたルールでマッピング処理を実行"""
    selected_rule = rules[selected_tab_index] if selected_tab_index < len(rules) else None

    if selected_rule:
        try:
            execute_mapping(company_name, management_number, selected_rule, company_db_path)
            messagebox.showinfo("成功", "マッピングが完了しました。")
        except MappingError as e:  # MappingErrorをキャッチ
            messagebox.showerror("エラー", f"マッピング中にエラーが発生しました: {e}") # エラーメッセージを表示
    else:
        raise MappingError("ルールが選択されていません。")