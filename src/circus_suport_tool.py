# === このファイルの責務（GPT用構造補助） ===
# このファイルは Circus支援ツールのランチャーUIを提供する
# 各種サブモジュール（台帳、マッピング、DB編集、ID生成など）をタブUIに統合する役割を担う

import sys
import os
import tkinter as tk
from tkinter import ttk

from ledger_creator import LedgerCreatorApp
from No_sakusei_fixed import InputUI, IdGenerator

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from kigyouDB import KigyouDBManager
from mapping_tool import MappingTool
from circusDB_viewer_edit import CircusDB_viewer_edit
from mapping_module import MappingToolUI

from cache_snapshot_utils import detect_snapshot_anomalies, restore_mapping_cache_from_csv
import glob

class CacheMonitorFrame(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.create_widgets()

    def create_widgets(self):
        btn_monitor = tk.Button(self, text="🕵️ 差分監視実行", command=self.run_monitoring)
        btn_monitor.pack(pady=5)
        btn_restore = tk.Button(self, text="♻️ 最新復元実行", command=self.restore_latest)
        btn_restore.pack(pady=5)

        self.text = tk.Text(self, wrap='none', height=30)
        scrollbar = tk.Scrollbar(self, command=self.text.yview)
        self.text.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    def run_monitoring(self):
        self.text.delete(1.0, tk.END)
        try:
            detect_snapshot_anomalies()
            self.text.insert(tk.END, "[OK] 差分監視完了\n")
        except Exception as e:
            self.text.insert(tk.END, f"[ERR] 差分監視中エラー: {e}\n")

    def restore_latest(self):
        self.text.delete(1.0, tk.END)
        try:
            files = sorted(glob.glob("cache/cache_snapshot_*.csv"))
            if not files:
                self.text.insert(tk.END, "スナップショットが存在しません\n")
                return
            latest = files[-1]
            restored = restore_mapping_cache_from_csv(latest)
            self.text.insert(tk.END, f"[OK] {len(restored)} 件 復元成功\n")
        except Exception as e:
            self.text.insert(tk.END, f"[ERR] 復元中エラー: {e}\n")

class CircusSupportTool:
    def __init__(self, root):
        self.root = root
        self.root.title("Circus Support Tool")
        self.root.geometry("1200x800")

        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # 企業DB管理
        try:
            KigyouDBManager.add_to_tab(self.notebook)
        except AttributeError:
            frame = ttk.Frame(self.notebook)
            self.notebook.add(frame, text="企業DB管理")
            KigyouDBManager(frame).pack(fill=tk.BOTH, expand=True)

        # マッピングツール
        try:
            MappingTool.add_to_tab(self.notebook)
        except AttributeError:
            frame = ttk.Frame(self.notebook)
            self.notebook.add(frame, text="マッピングツール")
            MappingTool(frame).pack(fill=tk.BOTH, expand=True)

        # Circus DB 編集ビューア
        try:
            CircusDB_viewer_edit.add_to_tab(self.notebook)
        except AttributeError:
            frame = ttk.Frame(self.notebook)
            self.notebook.add(frame, text="Circus DB 編集")
            CircusDB_viewer_edit(frame).pack(fill=tk.BOTH, expand=True)

        # マッピングプレビューUI
        try:
            frame = ttk.Frame(self.notebook)
            self.notebook.add(frame, text="マッピングプレビューUI")
            mapping_ui = MappingToolUI(frame, "circus_db.csv", "circus_db_mapping.csv")
            mapping_ui.pack(fill=tk.BOTH, expand=True)
        except Exception as e:
            print("MappingToolUI 起動エラー:", e)

        # LedgerCreator（管理台帳作成UI）
        try:
            frame = ttk.Frame(self.notebook)
            self.notebook.add(frame, text="管理台帳作成")
            LedgerCreatorApp(frame)  # pack不要
        except Exception as e:
            print("LedgerCreator 起動エラー:", e)

        # No_sakusei（ID発行UI）
        try:
            frame = ttk.Frame(self.notebook)
            self.notebook.add(frame, text="ID発行フォーム")
            id_generator = IdGenerator()
            InputUI(frame, id_generator)
        except Exception as e:
            print("No_sakusei 起動エラー:", e)

        # Cacheモニタータブ
        try:
            frame = ttk.Frame(self.notebook)
            self.notebook.add(frame, text="Cacheモニター")
            CacheMonitorFrame(frame).pack(fill=tk.BOTH, expand=True)
        except Exception as e:
            print("CacheMonitor 起動エラー:", e)

        # 終了ボタン（全モジュール共通）
        tk.Button(root, text="終了", command=root.destroy).pack(pady=10)
        # 起動時にキャッシュスナップショットの差分を監視
        try:
            detect_snapshot_anomalies()
        except Exception as e:
            print(f"[起動差分監視エラー] {e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = CircusSupportTool(root)
    root.mainloop()
