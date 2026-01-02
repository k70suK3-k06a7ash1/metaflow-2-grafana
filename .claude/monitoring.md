# 監視とメトリクス

## メトリクス収集フロー

```
Metaflow Flow
     │
     │ record_*()
     ▼
┌─────────────────┐
│ MetaflowMetrics │ (prometheus-client)
└─────────────────┘
     │
     │ push_to_gateway()
     ▼
┌─────────────────┐
│   Pushgateway   │ :9091
└─────────────────┘
     │
     │ scrape
     ▼
┌─────────────────┐
│   Prometheus    │ :9090
└─────────────────┘
     │
     │ query
     ▼
┌─────────────────┐
│    Grafana      │ :3000
└─────────────────┘
```

## 収集するメトリクス

### フローレベル
| メトリクス | 型 | 説明 |
|-----------|------|------|
| `metaflow_flow_runs_total` | Counter | フロー実行回数 |
| `metaflow_flow_run_duration_seconds` | Histogram | フロー実行時間 |

### ステップレベル
| メトリクス | 型 | 説明 |
|-----------|------|------|
| `metaflow_step_runs_total` | Counter | ステップ実行回数 |
| `metaflow_step_duration_seconds` | Histogram | ステップ実行時間 |

### MLメトリクス
| メトリクス | 型 | 説明 |
|-----------|------|------|
| `metaflow_model_accuracy` | Gauge | モデル精度 |
| `metaflow_training_loss` | Gauge | 訓練損失（エポック別） |

## 使用例

```python
from src.metrics import get_metrics

metrics = get_metrics()

# フロー開始/終了
start = metrics.record_flow_start("MyFlow")
# ... 処理 ...
metrics.record_flow_end("MyFlow", start, "success")

# エポックごとの損失
for epoch, loss in enumerate(history):
    metrics.record_training_loss(
        flow_name="MyFlow",
        step_name="train",
        epoch=epoch,
        loss=loss
    )

# モデル精度
metrics.record_model_metrics(
    flow_name="MyFlow",
    model_name="model_v1",
    accuracy=0.95
)
```

## Grafanaダッシュボード

プロビジョニングにより自動セットアップ:
- `grafana/dashboards/metaflow.json` - ダッシュボード定義
- `grafana/provisioning/datasources/` - Prometheusデータソース
- `grafana/provisioning/dashboards/` - ダッシュボードプロバイダ

## アラート設定例（PromQL）

```promql
# 成功率が90%を下回ったらアラート
sum(metaflow_flow_runs_total{status="success"})
/ sum(metaflow_flow_runs_total) < 0.9

# フロー実行時間が5分を超えたらアラート
histogram_quantile(0.95, metaflow_flow_run_duration_seconds_bucket) > 300
```
