# データフロー

## パイプライン実行フロー

```
PipelineConfig
      │
      ▼
┌─────────────┐
│  load_data  │ → Result[TrainingData, str]
└─────────────┘
      │ Success
      ▼
┌───────────────┐
│ validate_data │ → Result[TrainingData, str]
└───────────────┘
      │ Success
      ▼
┌──────────────────┐
│ preprocess_data  │ → Result[TrainingData, str]
└──────────────────┘
      │ Success
      ▼
┌─────────────┐
│ train_model │ → Result[TrainingResult, str]
└─────────────┘
      │ Success
      ▼
┌────────────────┐
│ evaluate_model │ → Result[ModelMetrics, str]
└────────────────┘
      │ Success
      ▼
PipelineResult
```

## エラー伝播

どのステップでFailureが発生しても、即座にパイプライン全体がFailureを返す。

```python
# 各ステップの戻り値
load_data()      → Success(TrainingData) or Failure("[Load] error")
validate_data()  → Success(TrainingData) or Failure("[Validate] error")
preprocess()     → Success(TrainingData) or Failure("[Preprocess] error")
train_model()    → Success(TrainingResult) or Failure("[Train] error")
evaluate()       → Success(ModelMetrics) or Failure("[Evaluate] error")
```

## Metaflow統合時のデータ保存

```python
@step
def run_pipeline(self):
    result = run_pipeline(self.config)

    match result:
        case Success(r):
            # Metaflowのselfに保存（永続化）
            self.accuracy = r.metrics.accuracy
            self.training_history = r.training.history

        case Failure(e):
            self.error_message = e
```

**ポイント**:
- Resultのunwrapは**Metaflow層でのみ**行う
- 下位層は常にResultを返す（unwrapしない）
