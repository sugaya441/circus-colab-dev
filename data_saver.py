# === このファイルの責務（GPT用構造補助） ===
# data_saver.py：
# 本ファイルは「最終的な保存処理（circus_db.csvへの出力）」を担う
# キャッシュ操作には一切関与しない（単発保存責務）

import pandas as pd
from datetime import datetime

REQUIRED_COLUMNS = [
    "企業名", "管理番号", "求人タイトル", "募集予定人数", "仕事内容", "PRポイント",
    "勤務地住所", "勤務時間補足", "勤務地・勤務時間_資料", "年収例", "給与条件補足", 
    "給与・賞与_資料", "休日休暇補足", "休日・休暇_資料", "福利厚生・諸手当", 
    "福利厚生・諸手当_資料", "応募時必須条件", "求める人材_資料", "成果報酬金額", 
    "支払いサイト", "返戻金規定", "手数料設定_資料"
]

def validate_df_structure(df):
    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing:
        raise ValueError(f"circus_db.csv に必要な列が不足しています: {missing}")

def save_circus_db(new_rows_df, circus_db_path="circus_db.csv", metadata=None):
    try:
        df_circus = pd.read_csv(circus_db_path, encoding='utf-8')
    except FileNotFoundError:
        df_circus = pd.DataFrame(columns=REQUIRED_COLUMNS)

    validate_df_structure(new_rows_df)

    for _, new_row in new_rows_df.iterrows():
        row_copy = new_row.copy()

        if metadata:
            for key, value in metadata.items():
                row_copy[key] = value

        mask = (df_circus['企業名'] == row_copy['企業名']) & (df_circus['管理番号'] == row_copy['管理番号'])
        duplicate_rows = df_circus[mask]
        if not ((duplicate_rows == row_copy).all(axis=1).any()):
            df_circus = df_circus[~mask]
            df_circus = pd.concat([df_circus, pd.DataFrame([row_copy])], ignore_index=True)

    df_circus.to_csv(circus_db_path, index=False, encoding='utf-8')