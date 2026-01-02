"""Model training functionality."""

import random
import time
from typing import Callable

from returns.result import Failure, Result, Success

from src.domain import PipelineConfig, TrainingData, TrainingResult


def train_model(
    data: TrainingData,
    config: PipelineConfig,
    on_epoch: Callable[[int, float], None] | None = None,
) -> Result[TrainingResult, str]:
    """Train a model on the preprocessed data.

    Args:
        data: Preprocessed training data.
        config: Pipeline configuration with training parameters.
        on_epoch: Optional callback called after each epoch with (epoch, loss).

    Returns:
        Success with TrainingResult or Failure with error message.
    """
    if not data.is_preprocessed:
        return Failure("Cannot train on unpreprocessed data")

    try:
        history: list[float] = []

        for epoch in range(config.epochs):
            # Simulate training time
            time.sleep(random.uniform(0.03, 0.08))

            # Simulate decreasing loss with some noise
            base_loss = 1.0 / (epoch + 1)
            noise = random.uniform(-0.05, 0.1)
            loss = max(0.01, base_loss + noise)

            history.append(loss)

            # Callback for progress reporting
            if on_epoch:
                on_epoch(epoch + 1, loss)

        return Success(
            TrainingResult(
                epochs=config.epochs,
                history=tuple(history),
                final_loss=history[-1],
            )
        )

    except Exception as e:
        return Failure(f"Training failed: {e}")
