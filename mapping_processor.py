# === このファイルの責務（GPT用構造補助） ===
# 本ファイルは「マッピングルールの適用処理」を担う
# 保存処理は data_saver.py に委譲され、本モジュールはDataFrameを構築して渡すのみとする

import pandas as pd
from data_saver import save_circus_db, validate_df_structure
from datetime import datetime

class MappingError(Exception):
    pass

def validate_rule(rule, row):
    for circus_col, company_col_template in rule.items():
        if company_col_template:
            try:
                company_col_template.format(**row)
            except KeyError:
                raise MappingError(f"テンプレート '{company_col_template}' に必要な列が存在しません。")

def apply_rule(rule, row):
    new_data = {}
    for circus_col, company_col_template in rule.items():
        if company_col_template:
            try:
                new_data[circus_col] = company_col_template.format(**row)
            except KeyError:
                new_data[circus_col] = ""
        else:
            new_data[circus_col] = ""
    return new_data

def execute_mapping(company_name, management_number, rule, company_db_path):
    try:
        df_company = pd.read_csv(company_db_path, encoding="utf-8-sig")
    except FileNotFoundError:
        raise MappingError(f"{company_db_path} が見つかりません。")
    except Exception as e:
        raise MappingError(f"企業データ読み込み中にエラー: {e}")

    if df_company.empty:
        raise MappingError("企業データが空です。")

    try:
        validate_rule(rule, df_company.iloc[0])
    except MappingError as e:
        raise e

    new_row = apply_rule(rule, df_company.iloc[0])
    new_row["企業名"] = company_name
    new_row["管理番号"] = management_number
    return pd.DataFrame([new_row])

def execute_mapping_with_rules(company_name, management_number, rules, company_db_path, selected_rule_index):
    if selected_rule_index < 0 or selected_rule_index >= len(rules):
        raise MappingError("有効なルールが選択されていません。")

    selected_rule = rules[selected_rule_index]
    df_circus = execute_mapping(company_name, management_number, selected_rule, company_db_path)

    # メタデータ付加
    metadata = {
        "ルールNo.": selected_rule_index + 1,
        "マッピング識別": f"{company_name}_{management_number}",
        "マッピング日時": datetime.now().isoformat()
    }

    validate_df_structure(df_circus)
    save_circus_db(df_circus, overwrite_keys=("企業名", "管理番号"), metadata=metadata)
