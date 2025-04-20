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

        # サブウインドウ：終了ラベル専用
        exit_window = tk.Toplevel(self.root)
        exit_window.overrideredirect(True)
        exit_window.attributes('-topmost', True)

        # 配置
        self.root.update_idletasks()
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        window_width, window_height = 160, 60
        x = screen_width // 2 - window_width // 2
        y = screen_height - window_height - 50
        exit_window.geometry(f"{window_width}x{window_height}+{x}+{y}")

        # ラベルで擬似ボタン
        exit_label = tk.Label(exit_window, text="🛑 終了", font=("Arial", 12, "bold"),
                              bg="lightgray", relief="raised", bd=2, padx=10, pady=10)
        exit_label.pack(expand=True, fill=tk.BOTH)

        # 終了判定用フラグ
        exit_window._allow_exit = True

        # --- イベント処理 ---
        def on_button_press(event):
            # Ctrl (0x0004) + Shift (0x0001)
            if event.state & 0x0004 and event.state & 0x0001:
                exit_window._allow_exit = False
                exit_window._drag_start_x = event.x
                exit_window._drag_start_y = event.y
                exit_window._drag_mode = True
            else:
                exit_window._allow_exit = True
                exit_window._drag_mode = False

        def on_motion(event):
            if getattr(exit_window, "_drag_mode", False):
                dx = event.x - exit_window._drag_start_x
                dy = event.y - exit_window._drag_start_y
                new_x = exit_window.winfo_x() + dx
                new_y = exit_window.winfo_y() + dy
                exit_window.geometry(f"+{new_x}+{new_y}")

        def on_release(event):
            if getattr(exit_window, "_allow_exit", True):
                exit_label.config(bg="red")
                self.root.after(100, self.root.destroy)

        # バインディング
        exit_label.bind("<ButtonPress-1>", on_button_press)
        exit_label.bind("<B1-Motion>", on_motion)
        exit_label.bind("<ButtonRelease-1>", on_release)


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
            # タブに追加するためのフレームを作成し、この中にCircusDB_viewer_editを配置
            frame = ttk.Frame(self.notebook)
            self.notebook.add(frame, text="Circus DB 編集")
            
            # CircusDB_viewer_editを作成し、フレーム内に適切に配置
            # フレームの内部に合わせて完全に拡張されるようにpackオプションを調整
            circusDB_editor = CircusDB_viewer_edit(frame)
            
            # 上下左右の余白を無くすために、padxとpadyを0に設定
            circusDB_editor.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)
            
            # フレーム自体のサイズも調整
            frame.pack_propagate(False)

        # マッピングプレビューUI
        try:
            frame = ttk.Frame(self.notebook)
            self.notebook.add(frame, text="マッピングプレビューUI")
            mapping_ui = MappingToolUI(frame, "circus_db.csv", "circus_db_mapping.csv")
            mapping_ui.pack(fill=tk.BOTH, expand=True)
            ledger_app.main_frame.pack(fill=tk.BOTH, expand=True)
        except Exception as e:
            print("MappingToolUI 起動エラー:", e)

        # LedgerCreator（管理台帳作成UI）
        try:
            frame = ttk.Frame(self.notebook)
            self.notebook.add(frame, text="管理台帳作成")
            ledger_app = LedgerCreatorApp(frame)
        except Exception as e:
            print(f"LedgerCreator 起動エラー: {e}")
            import traceback
            traceback.print_exc()

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

        # 起動時にキャッシュスナップショットの差分を監視
        try:
            detect_snapshot_anomalies()
        except Exception as e:
            print(f"[起動差分監視エラー] {e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = CircusSupportTool(root)
    root.mainloop()