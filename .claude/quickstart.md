# クイックスタート

## 前提条件

- Python 3.11+
- Docker & Docker Compose
- uv (`curl -LsSf https://astral.sh/uv/install.sh | sh`)

## セットアップ

```bash
# 1. 依存関係インストール
uv sync

# 2. Docker環境起動
docker compose up -d

# 3. 環境変数設定（オプション）
cp .env.example .env
```

## フロー実行

```bash
# MLトレーニングフロー実行
uv run python src/flows/ml_training.py run
```

## 確認

| サービス | URL | 認証 |
|----------|-----|------|
| Grafana | http://localhost:3000 | admin/admin |
| Prometheus | http://localhost:9090 | - |
| Pushgateway | http://localhost:9091 | - |

## Grafanaで確認

1. http://localhost:3000 を開く
2. admin/admin でログイン
3. Dashboards → "Metaflow Pipeline Monitoring"

## トラブルシューティング

### Pushgatewayに接続できない
```bash
# Pushgatewayが起動しているか確認
docker compose ps

# ログ確認
docker compose logs pushgateway
```

### メトリクスが表示されない
```bash
# Pushgatewayにデータがあるか確認
curl http://localhost:9091/metrics

# Prometheusでスクレイプされているか確認
# http://localhost:9090/targets
```

### フローがエラーになる
```bash
# Metaflowのログを確認
uv run python src/flows/ml_training.py run --help
```

## 停止

```bash
docker compose down
```
