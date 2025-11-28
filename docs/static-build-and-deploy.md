# 静的ビルドと BirdXplorer_Viewer へのデプロイ手順

このドキュメントでは、kouchou-ai クライアントを静的ビルドし、BirdXplorer_Viewer の iframe で表示するための手順を説明します。

## 前提条件

- Docker Compose でサーバーが起動していること (`docker compose up`)
- API サーバーが `http://localhost:8000` で稼働していること（デフォルト設定）
- ビルド対象のレポートが `READY` 状態であること

> **注意**: API サーバーのポートが `.env` ファイルでカスタマイズされている場合は、以下のコマンドの `8000` を適切なポート番号に置き換えてください。

## 手順

### 1. 静的ビルドを実行

```bash
# BirdXplorer_kouchou-ai のルートディレクトリに移動
cd <BirdXplorer_kouchou-ai のパス>

# API サーバーが起動していることを確認
curl -I http://localhost:8000/healthcheck

# 静的ビルドを実行（特定のスラッグのみビルドする場合）
cd client
BUILD_SLUGS="<ビルドしたいレポートのスラッグ>" \
NEXT_PUBLIC_API_BASEPATH=http://localhost:8000 \
API_BASEPATH=http://localhost:8000 \
NEXT_PUBLIC_PUBLIC_API_KEY=public \
NEXT_PUBLIC_STATIC_EXPORT_BASE_PATH="/kouchou-ai" \
npm run build:static

# すべてのレポートをビルドする場合は BUILD_SLUGS を省略
```

### 2. ビルド結果を BirdXplorer_Viewer にコピー

```bash
# 既存のディレクトリを削除
rm -rf <BirdXplorer_Viewer のパス>/public/kouchou-ai

# 新しいビルド結果をコピー
cp -r <BirdXplorer_kouchou-ai のパス>/client/out \
     <BirdXplorer_Viewer のパス>/public/kouchou-ai
```

### 3. BirdXplorer_Viewer で確認

```bash
cd <BirdXplorer_Viewer のパス>

# 開発サーバーを起動（既に起動している場合は不要）
pnpm run dev
```

ブラウザで以下を確認：

- `http://localhost:5174/test-iframe` - iframe で埋め込み表示

> **注意**: `/kouchou-ai/` 配下のパスに直接アクセスすると、BirdXplorer_Viewer のルーティングと競合する可能性があります。必ず `/test-iframe` ページから iframe 経由で確認してください。

## トラブルシューティング

### ビルドが失敗する場合

1. API サーバーが起動しているか確認

   ```bash
   curl http://localhost:8000/reports
   ```

2. レポートが `READY` 状態か確認

   ```bash
   curl -H "x-api-key: public" http://localhost:8000/reports
   ```

3. `generateStaticParams` がスラッグを取得できない場合
   - `BUILD_SLUGS` 環境変数で明示的にスラッグを指定

### CSS や Chart が表示されない場合

- `NEXT_PUBLIC_STATIC_EXPORT_BASE_PATH="/kouchou-ai"` が設定されているか確認
- iframe の `sandbox` 属性に `allow-same-origin` が含まれているか確認
  ```tsx
  <iframe
    sandbox="allow-scripts allow-popups allow-forms allow-same-origin"
    src="/kouchou-ai/<スラッグ>/"
  />
  ```

### 権限エラーが発生する場合

- `client/.next` や `client/out` ディレクトリが root 権限で作成されている場合
  ```bash
  sudo rm -rf client/.next client/out
  ```

## 環境変数の説明

静的ビルド用の環境変数は、`.env` ファイルではなく**コマンドライン引数として指定することを推奨**します。これらは一時的なビルド設定であり、通常の開発環境とは異なる値を使用するためです。

| 変数名                                | 説明                                            | 例                      | 推奨設定方法       |
| ------------------------------------- | ----------------------------------------------- | ----------------------- | ------------------ |
| `BUILD_SLUGS`                         | ビルドするレポートのスラッグ（カンマ区切り）    | `"slug1,slug2"`         | コマンドライン指定 |
| `NEXT_PUBLIC_API_BASEPATH`            | クライアントサイドで使用する API エンドポイント | `http://localhost:8000` | コマンドライン指定 |
| `API_BASEPATH`                        | サーバーサイドで使用する API エンドポイント     | `http://localhost:8000` | コマンドライン指定 |
| `NEXT_PUBLIC_PUBLIC_API_KEY`          | 公開 API キー                                   | `public`                | コマンドライン指定 |
| `NEXT_PUBLIC_STATIC_EXPORT_BASE_PATH` | 静的ファイルのベースパス                        | `/kouchou-ai`           | コマンドライン指定 |

> **重要**: これらの環境変数を `.env` ファイルに追加すると、通常の開発環境に影響を与える可能性があります。静的ビルド時のみ、上記の手順に従ってコマンドラインで指定してください。

## 参考情報

- 静的ビルドの設定: `client/next.config.ts`
- ビルドスクリプト: `client/package.json` の `build:static`
- ファイルリネーム: `client/scripts/rename-file.mjs`
- 画像コピー: `client/scripts/copy-image.mjs`
