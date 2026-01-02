"""Domain models representing core entities in the ML pipeline.

These are pure data classes with no business logic.
They define the shape of data flowing through the pipeline.
"""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class PipelineConfig:
    """Configuration for pipeline execution."""

    samples: int = 50000
    features: int = 50
    epochs: int = 10
    batch_size: int = 32
    learning_rate: float = 0.001


@dataclass(frozen=True)
class TrainingData:
    """Immutable training data container."""

    samples: int
    features: int
    is_validated: bool = False
    is_preprocessed: bool = False


@dataclass(frozen=True)
class TrainingResult:
    """Immutable training result container."""

    epochs: int
    history: tuple[float, ...]  # Immutable tuple instead of list
    final_loss: float

    @property
    def best_loss(self) -> float:
        """Return the minimum loss achieved during training."""
        return min(self.history) if self.history else float("inf")


@dataclass(frozen=True)
class ModelMetrics:
    """Immutable model evaluation metrics."""

    accuracy: float
    precision: float
    recall: float
    f1_score: float

    def to_dict(self) -> dict[str, float]:
        """Convert metrics to dictionary."""
        return {
            "accuracy": self.accuracy,
            "precision": self.precision,
            "recall": self.recall,
            "f1_score": self.f1_score,
        }


@dataclass(frozen=True)
class PipelineResult:
    """Complete pipeline execution result."""

    data: TrainingData
    training: TrainingResult
    metrics: ModelMetrics
    success: bool = True
    error_message: str | None = None

    @classmethod
    def failure(cls, error: str) -> "PipelineResult":
        """Create a failed pipeline result."""
        return cls(
            data=TrainingData(samples=0, features=0),
            training=TrainingResult(epochs=0, history=(), final_loss=float("inf")),
            metrics=ModelMetrics(accuracy=0, precision=0, recall=0, f1_score=0),
            success=False,
            error_message=error,
        )
