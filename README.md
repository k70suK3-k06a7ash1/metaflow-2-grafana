# Metaflow to Grafana Integration

MetaflowとGrafanaを連携させたMLパイプライン監視システム

## アーキテクチャ

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Metaflow      │────▶│  Pushgateway    │────▶│   Prometheus    │
│   (ML Pipeline) │     │  (Metrics Push) │     │  (Time Series)  │
└─────────────────┘     └─────────────────┘     └────────┬────────┘
                                                         │
                                                         ▼
                                                ┌─────────────────┐
                                                │    Grafana      │
                                                │  (Dashboards)   │
                                                └─────────────────┘
```

## なぜこのスタック？

| ツール | 得意なこと | 苦手なこと |
|--------|-----------|-----------|
| **Metaflow** | MLパイプラインの実行管理、データの版管理、Pythonicな開発体験 | システム全体のリアルタイム監視、長期的なメトリクス可視化 |
| **Grafana** | インフラ・アプリの横断的監視、ダッシュボード、アラート通知 | 複雑な計算グラフの管理、機械学習の実験管理 |

それぞれの得意分野を補完し合う関係にあるため、この組み合わせは合理的です。

## 必要要件

- Python 3.11+
- Docker & Docker Compose
- uv (Python パッケージマネージャー)

## セットアップ

### 1. Python環境の構築

```bash
# uvをインストール（未インストールの場合）
curl -LsSf https://astral.sh/uv/install.sh | sh

# プロジェクトの依存関係をインストール
uv sync
```

### 2. Docker環境の起動

```bash
# Grafana, Prometheus, Pushgatewayを起動
docker compose up -d
```

### 3. 環境変数の設定

```bash
cp .env.example .env
# 必要に応じて.envを編集
```

## 使い方

### Metaflow フローの実行

```bash
# MLトレーニングフローを実行
uv run python src/flows/ml_training.py run
```

### Grafanaダッシュボードへのアクセス

1. ブラウザで http://localhost:3000 を開く
2. ログイン: `admin` / `admin`
3. "Metaflow Pipeline Monitoring" ダッシュボードを開く

### プログラムでGrafanaを操作

```python
from src.grafana_manager import GrafanaManager

# Grafanaに接続
manager = GrafanaManager(
    host="localhost",
    port=3000,
    username="admin",
    password="admin"
)

# ヘルスチェック
print(manager.health_check())

# ダッシュボード一覧
dashboards = manager.list_dashboards()
```

### カスタムメトリクスの記録

```python
from src.metrics import get_metrics

metrics = get_metrics()

# モデルの精度を記録
metrics.record_model_metrics(
    flow_name="MyFlow",
    model_name="my_model",
    accuracy=0.95
)

# 訓練損失を記録
metrics.record_training_loss(
    flow_name="MyFlow",
    step_name="train",
    epoch=1,
    loss=0.5
)
```

## 構成

```
.
├── docker-compose.yml          # Docker Compose設定
├── pyproject.toml              # Python依存関係 (uv + returns)
├── .claude/                    # Claude Code スキル
├── grafana/
│   ├── dashboards/             # Grafanaダッシュボード
│   └── provisioning/           # 自動プロビジョニング
├── prometheus/
│   └── prometheus.yml          # Prometheus設定
└── src/
    ├── domain/                 # ドメインモデル (純粋データ)
    │   └── models.py           # TrainingData, ModelMetrics, etc.
    ├── data/                   # データ処理層
    │   ├── loader.py           # データロード
    │   ├── validator.py        # バリデーション
    │   └── preprocessor.py     # 前処理
    ├── training/               # トレーニング層
    │   ├── trainer.py          # モデル訓練
    │   └── evaluator.py        # モデル評価
    ├── pipeline/               # パイプライン層 (Returns統合)
    │   └── runner.py           # Result monadで合成
    ├── flows/                  # Metaflowオーケストレーション層
    │   └── ml_training.py      # MLTrainingFlow
    ├── metrics.py              # Prometheusメトリクス
    └── grafana_manager.py      # Grafana API管理
```

## セマンティック境界

| レイヤー | 責務 | 技術 |
|----------|------|------|
| **domain** | データモデル定義 | dataclass (frozen) |
| **data** | データI/O・変換 | Returns Result |
| **training** | ML処理 | Returns Result |
| **pipeline** | 関数合成・エラー伝播 | Returns bind/map |
| **flows** | 実行オーケストレーション | Metaflow @step |
| **metrics** | 可観測性 | Prometheus |

## アクセスポイント

| サービス | URL |
|----------|-----|
| Grafana | http://localhost:3000 |
| Prometheus | http://localhost:9090 |
| Pushgateway | http://localhost:9091 |

## 停止

```bash
docker compose down
```

データを削除する場合:

```bash
docker compose down -v
```
