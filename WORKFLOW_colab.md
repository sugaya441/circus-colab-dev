
# WORKFLOW_colab.md

## 📦 リポジトリ構成

- `/src/` にすべての Python ファイルを格納
- Colab ノートブックから import しやすい構成
- プロンプトはルートディレクトリに保持

## 🧑‍💻 Colab での使用手順

1. Google Colab を開く
2. `!git clone https://github.com/your-username/circus-colab-dev.git`
3. `sys.path.append("/content/circus-colab-dev/src")` を記述
4. 任意のモジュールを `import` して開発

## ✅ コーディングルール

- 一括置換は全面禁止（関数・変数単位も含む）
- 文法・構文・処理フロー・既存機能の正常性を全チェック
- 影響のある全ファイルを必ず確認

## 🧠 くじらプロンプトに基づく行動原則

- 指示は100％厳守、500％実行を目標
- 動作・修正ごとに確認と報告を明確化
- 修正の根拠と影響を説明できること
