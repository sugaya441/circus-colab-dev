# === cache_snapshot_utils.py ===
# Step C: スナップショット監視処理 + Step D: CSV → キャッシュ復元処理
import os
import glob
import pandas as pd

# === Step C: 差分監視チェック ===
def detect_snapshot_anomalies(cache_dir="cache"):
    try:
        files = sorted(glob.glob(os.path.join(cache_dir, "cache_snapshot_*.csv")))
        if len(files) < 2:
            print("[monitor] 差分検出には最低2つのスナップショットが必要です")
            return
        latest, previous = files[-1], files[-2]
        df1 = pd.read_csv(previous)
        df2 = pd.read_csv(latest)
        if df1.equals(df2):
            print("[monitor] 差分なし（スナップショット内容は同一です）")
        else:
            print("[monitor] 差分検出：最新スナップショットと前回に違いがあります")
            print(f"前回: {previous}, 現在: {latest}")
            print(f"前回行数: {len(df1)}, 現在行数: {len(df2)}")
    except Exception as e:
        print(f"[monitor] 差分チェックエラー: {e}")

# === Step D: CSV → キャッシュ復元 ===
def restore_mapping_cache_from_csv(csv_path):
    try:
        df = pd.read_csv(csv_path)
        mapping_cache = {}
        for idx, row in df.iterrows():
            entry = row.dropna().to_dict()
            key = str(entry.get("No.", f"auto_{idx}"))
            mapping_cache[key] = entry
        print(f"[restore] CSVから {len(mapping_cache)} 件のキャッシュを復元しました")
        return mapping_cache
    except Exception as e:
        print(f"[restore] 復元エラー: {e}")
        return {}
