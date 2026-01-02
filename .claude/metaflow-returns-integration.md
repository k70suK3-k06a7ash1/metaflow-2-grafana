# Metaflow + Returns 統合パターン

MetaflowとReturns（Pythonのモナドパッケージ）を組み合わせる際のベストプラクティス。

## 設計思想

- **Metaflow:** インフラ、並列実行、データの永続化、リトライ（マクロな視点）
- **Returns:** 型安全性、エラーハンドリング、純粋関数（ミクロな視点）

## 推奨パターン：ビジネスロジックの分離

Metaflowの `@step` 内で直接モナドを扱うのではなく、**ロジックを純粋関数としてReturnsで書き、Metaflowはオーケストレーターに徹する**。

```python
from returns.result import Result, Success, Failure
from returns.pipeline import flow
from metaflow import FlowSpec, step

# ロジック層（純粋関数）
def validate_data(data: dict) -> Result[dict, str]:
    if not data:
        return Failure("Empty data")
    return Success(data)

def process_data(data: dict) -> Result[dict, str]:
    try:
        processed = transform(data)
        return Success(processed)
    except Exception as e:
        return Failure(str(e))

def train_model(data: dict) -> Result[Model, str]:
    try:
        model = Model().fit(data)
        return Success(model)
    except Exception as e:
        return Failure(str(e))

# パイプライン関数
def ml_pipeline(data: dict) -> Result[Model, str]:
    return flow(
        data,
        validate_data,
        process_data,
        train_model,
    )

# Metaflow層（オーケストレーター）
class MLFlow(FlowSpec):
    @step
    def start(self):
        result = ml_pipeline(self.input_data)
        
        match result:
            case Success(model):
                self.model = model
                self.next(self.end)
            case Failure(error):
                self.error_msg = error
                self.next(self.handle_error)
```

## 使い分け

| シーン | 推奨 |
|--------|------|
| 複雑なデータバリデーション | `Result`, `Maybe` |
| 外部API連携（リトライ/タイムアウト） | `Result`, `IO` |
| オプショナル値の連鎖 | `Maybe` |
| 非同期処理 | `FutureResult` |

## アンチパターン

```python
# ❌ 悪い例：Metaflowの中でReturnsを中途半端に使う
@step
def train(self):
    result = train_model(self.data)
    if isinstance(result, Success):
        self.model = result.unwrap()  # selfに代入するので恩恵が薄い
```

## メリット

- 失敗に強いMLパイプライン
- 失敗理由が明確（デバッグ容易）
- 型安全なエラーハンドリング
- `try-except`の連鎖を回避
