# Docker環境セットアップ

## コンテナ構成

```
┌─────────────────────────────────────────────────────────┐
│                    Docker Network: monitoring           │
│                                                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │
│  │   Grafana   │  │ Prometheus  │  │ Pushgateway │     │
│  │   :3000     │  │   :9090     │  │   :9091     │     │
│  └─────────────┘  └─────────────┘  └─────────────┘     │
│         │                │                │             │
│         └────────────────┴────────────────┘             │
│                          │                              │
└──────────────────────────┼──────────────────────────────┘
                           │
              ┌────────────┴────────────┐
              │   Host Machine (uv)     │
              │   - Metaflow            │
              │   - Python app          │
              └─────────────────────────┘
```

## サービス詳細

### Grafana
- **イメージ**: `grafana/grafana:11.4.0`
- **ポート**: 3000
- **認証**: admin/admin
- **ボリューム**:
  - `grafana-data` - データ永続化
  - `./grafana/provisioning/` - 自動設定
  - `./grafana/dashboards/` - ダッシュボードJSON

### Prometheus
- **イメージ**: `prom/prometheus:v3.1.0`
- **ポート**: 9090
- **設定**: `./prometheus/prometheus.yml`
- **スクレイプ間隔**: 15秒

### Pushgateway
- **イメージ**: `prom/pushgateway:v1.10.0`
- **ポート**: 9091
- **用途**: バッチジョブからのメトリクスPush

## コマンド

```bash
# 起動
docker compose up -d

# ログ確認
docker compose logs -f grafana

# 停止
docker compose down

# データ含めて削除
docker compose down -v

# 再ビルド
docker compose up -d --build
```

## ネットワーク

コンテナ間は`monitoring`ブリッジネットワークで通信:
- Grafana → Prometheus: `http://prometheus:9090`
- Prometheus → Pushgateway: `http://pushgateway:9091`

ホストからは`localhost`でアクセス:
- Grafana: `http://localhost:3000`
- Prometheus: `http://localhost:9090`
- Pushgateway: `http://localhost:9091`

## 環境変数

```bash
# .env
PUSHGATEWAY_URL=localhost:9091
GRAFANA_HOST=localhost
GRAFANA_PORT=3000
GRAFANA_USER=admin
GRAFANA_PASSWORD=admin
```
