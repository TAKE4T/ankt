# 漢方AI診断システム

AIが症状に基づいて漢方診断を行い、最適な生薬を提案するチャットボットアプリケーションです。

![漢方AI診断システム](https://img.shields.io/badge/漢方-AI診断システム-green)
![Next.js](https://img.shields.io/badge/Next.js-15.4.4-black)
![Python](https://img.shields.io/badge/Python-3.9+-blue)
![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4-orange)

## ✨ 特徴

- 🤖 **構造化質問システム**: shindanファイルに基づく段階的な症状ヒアリング
- 📊 **高精度診断**: 27種類の症状データ（M1-M11, F1-F16）による詳細分析
- 🌿 **個別レシピ提案**: 3つの専用治療法から最適なものを選択
  - リズム巡り蒸し（ホルモン・血の不調）
  - デトックス蒸し（免疫・水の不調）
  - 安眠ゆるり蒸し（自律神経・精の不調）
- 💊 **詳細な生薬解説**: 各治療法に対応した生薬の効能と使用方法
- 📱 **レスポンシブデザイン**: モバイル・デスクトップ対応

## 🛠 技術スタック

- **フロントエンド**: Next.js 14, React, TypeScript, Tailwind CSS
- **バックエンド**: Python, FastAPI, LangChain, OpenAI GPT-4 API
- **デプロイ**: AWS Amplify
- **データ**: JSON形式の症状・診断データベース

## 🚀 クイックスタート

### 前提条件

- Node.js 18以上
- Python 3.9以上
- OpenAI APIキー

### 1. リポジトリのクローン

```bash
git clone https://github.com/TAKE4T/ankt.git
cd ankt/kanpo-ai
```

### 2. フロントエンドのセットアップ

```bash
npm install
```

### 3. バックエンドのセットアップ

```bash
cd backend
pip install -r requirements.txt

# 環境変数の設定
cp .env.example .env
# .envファイルを編集してOpenAI APIキーを設定
```

### 4. アプリケーションの起動

**ターミナル1 (バックエンド):**
```bash
cd backend
python main.py
```

**ターミナル2 (フロントエンド):**
```bash
npm run dev
```

**アクセス:** http://localhost:3000

## 📋 環境変数

`backend/.env`ファイルに以下を設定:

```env
OPENAI_API_KEY=your_openai_api_key_here
DEBUG=True
ENVIRONMENT=development
```

## 🏗 診断システムアーキテクチャ

### 診断フロー

1. **基本症状ヒアリング** - 疲労感、睡眠状態
2. **カテゴリ別詳細質問** - ホルモン、自律神経、免疫等
3. **症状スコア計算** - キーワードマッチングによる定量化
4. **診断ロジック適用** - shindanファイルのルールに基づく判定
5. **レシピ提案** - 最適な漢方治療法の推奨

### 診断ルール

- **Rule 001**: 単一レシピ推奨（2点以上の差）
- **Rule 002**: 複数レシピ混合推奨（1点以内の拮抗）
- **Rule 003**: 低スコア時の再質問促進
- **Rule 004**: カテゴリスコア合算による判定

## 📊 データ構造

### 症状データ (shojo.json)
```json
{
  "id": "M1",
  "title": "寝つきが悪く、夜中に目が覚める",
  "functions": ["自律神経"],
  "related_recipe": ["安眠ゆるり蒸し"]
}
```

### 診断データ (shindan.json)
```json
{
  "title": "リズム巡り蒸し",
  "categories": ["ホルモン", "血虚", "瘀血"],
  "herbs": ["よもぎ", "当帰", "紅花", "玫瑰花", "陳皮"],
  "description": "血流を促進し、ホルモンバランスを整える蒸しケア"
}
```

## 🔗 API エンドポイント

| エンドポイント | メソッド | 説明 |
|---|---|---|
| `/` | GET | システム情報 |
| `/chat` | POST | チャット対話処理 |
| `/health` | GET | ヘルスチェック |

## 🚀 デプロイ

### 🎯 オプション1: AWS Amplify フルスタック (推奨)

**1. AWS Amplify Console**
1. https://console.aws.amazon.com/amplify/ にアクセス
2. 「New app」→「Host web app」を選択
3. GitHub接続後、`TAKE4T/ankt` リポジトリを選択

**2. アプリ設定**
- **App name**: `kanpo-ai`
- **Environment**: `main`
- **Build settings**: 自動検出（amplify.ymlを使用）

**3. 環境変数設定**
- `OPENAI_API_KEY`: あなたのOpenAI APIキー
- `ENVIRONMENT`: `production`

**4. デプロイ実行**
- 設定を保存してビルド開始
- フロントエンド + バックエンド（Lambda）が自動デプロイ

### 🎯 オプション2: Serverless Framework

```bash
# Serverless CLI インストール
npm install -g serverless

# AWS認証設定
serverless config credentials --provider aws --key YOUR_KEY --secret YOUR_SECRET

# バックエンドデプロイ
cd backend
serverless deploy

# フロントエンドは別途AWS Amplifyでデプロイ
```

### 🎯 オプション3: 分離デプロイ

バックエンドは以下のサービスでデプロイできます：

**Heroku:**
```bash
# Herokuアプリ作成
heroku create your-kanpo-backend

# 環境変数設定
heroku config:set OPENAI_API_KEY=your_api_key

# デプロイ
git subtree push --prefix=kanpo-ai/backend heroku main
```

**AWS Lambda + API Gateway:**
- Serverless Frameworkを使用してデプロイ
- 詳細は [Serverless公式ドキュメント](https://www.serverless.com/) を参照

**Docker + AWS ECS:**
```dockerfile
# backend/Dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["python", "main.py"]
```

## 🤝 貢献

1. このリポジトリをフォーク
2. 新しいブランチを作成 (`git checkout -b feature/amazing-feature`)
3. 変更をコミット (`git commit -m 'Add amazing feature'`)
4. ブランチにプッシュ (`git push origin feature/amazing-feature`)
5. Pull Requestを作成

## 📄 ライセンス

MIT License - 詳細は [LICENSE](LICENSE) ファイルを参照

## 🙏 謝辞

- OpenAI GPT-4 API
- LangChain Framework
- Next.js Framework
- Tailwind CSS

---

**注意**: このシステムは健康相談の補助ツールです。深刻な症状がある場合は、必ず医療専門家にご相談ください。