# セマンティック境界によるモジュール分割

## 原則

コードを「何をするか」ではなく「どの責務に属するか」で分割する。

## レイヤー構造

```
src/
├── domain/      # 何を扱うか (What)
├── data/        # どこから取得するか (Where)
├── training/    # どう処理するか (How - ML)
├── pipeline/    # どう組み合わせるか (Composition)
├── flows/       # いつ実行するか (When)
└── metrics/     # どう観測するか (Observe)
```

## 各レイヤーの責務

### domain/ - ドメインモデル層
- **責務**: ビジネスエンティティの定義
- **特徴**: 純粋データ、ロジックなし、不変 (frozen dataclass)
- **依存**: なし（最下層）

```python
@dataclass(frozen=True)
class TrainingData:
    samples: int
    features: int
    is_validated: bool = False
```

### data/ - データ処理層
- **責務**: データのI/O、変換、検証
- **特徴**: 外部リソースとの境界
- **依存**: domain

```python
def load_data(config) -> Result[TrainingData, str]:
    ...
def validate_data(data) -> Result[TrainingData, str]:
    ...
```

### training/ - トレーニング層
- **責務**: ML固有の処理（訓練、評価）
- **特徴**: 計算集約的な処理
- **依存**: domain

```python
def train_model(data, config) -> Result[TrainingResult, str]:
    ...
def evaluate_model(data, training) -> Result[ModelMetrics, str]:
    ...
```

### pipeline/ - パイプライン層
- **責務**: 処理ステップの合成、エラー伝播
- **特徴**: Returns Resultによる関数合成
- **依存**: data, training, domain

```python
def run_pipeline(config) -> Result[PipelineResult, str]:
    return (
        load_data(config)
        .bind(validate_data)
        .bind(preprocess_data)
        .bind(lambda d: train_model(d, config))
        ...
    )
```

### flows/ - フロー層
- **責務**: 実行オーケストレーション
- **特徴**: Metaflowステップ定義、メトリクス記録
- **依存**: pipeline, metrics

```python
class MLTrainingFlow(FlowSpec):
    @step
    def run_pipeline(self):
        result = run_pipeline(self.config)
        match result:
            case Success(r): self.next(self.end)
            case Failure(e): self.next(self.error)
```

## 依存関係の方向

```
flows ──→ pipeline ──→ training ──→ domain
              │                        ↑
              └──→ data ───────────────┘
```

**ルール**: 矢印の方向にのみ依存可能（逆方向は禁止）

## 境界を越えるデータ

- 層間のデータ受け渡しは必ず **domain モデル** を使用
- 生のdict/tupleでの受け渡しは禁止
- これにより型安全性と可読性を確保
