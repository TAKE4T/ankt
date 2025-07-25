# 漢方AI診断システム - バックエンドAPI

FastAPI + LangChain + OpenAI GPT-4を使用した漢方診断システムのバックエンドAPIです。

## 🚀 デプロイ

### Heroku

```bash
# Herokuアプリ作成
heroku create kanpo-ai-backend

# 環境変数設定
heroku config:set OPENAI_API_KEY=your_openai_api_key_here

# デプロイ
git push heroku main
```

### ローカル開発

```bash
# 依存関係インストール
pip install -r requirements.txt

# 環境変数設定
cp .env.example .env
# .envファイルを編集

# サーバー起動
python main.py
```

## 📋 環境変数

```env
OPENAI_API_KEY=your_openai_api_key_here
DEBUG=True
ENVIRONMENT=production
```

## 🔗 API エンドポイント

- `GET /` - システム情報
- `POST /chat` - チャット対話処理
- `GET /health` - ヘルスチェック

## 📊 データファイル

- `shojo.json` - 症状データ（M1-M11, F1-F16）
- `shindan.json` - 診断・レシピデータ