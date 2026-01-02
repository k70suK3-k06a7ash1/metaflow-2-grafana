"""Model evaluation functionality."""

import random
import time

from returns.result import Failure, Result, Success

from src.domain import ModelMetrics, TrainingData, TrainingResult


def evaluate_model(
    data: TrainingData,
    training: TrainingResult,
) -> Result[ModelMetrics, str]:
    """Evaluate the trained model on test data.

    Args:
        data: Training data (contains test split in real scenario).
        training: Training result with model state.

    Returns:
        Success with ModelMetrics or Failure with error message.
    """
    if training.epochs == 0:
        return Failure("Cannot evaluate untrained model")

    try:
        # Simulate evaluation time
        time.sleep(random.uniform(0.05, 0.15))

        # Simulate metrics (in real scenario, would evaluate on test set)
        # Better training (lower loss) correlates with better metrics
        loss_factor = 1 - min(training.final_loss, 0.9)

        accuracy = 0.7 + (0.28 * loss_factor) + random.uniform(-0.02, 0.02)
        precision = 0.68 + (0.28 * loss_factor) + random.uniform(-0.02, 0.02)
        recall = 0.65 + (0.30 * loss_factor) + random.uniform(-0.02, 0.02)

        # Clamp to valid range
        accuracy = max(0, min(1, accuracy))
        precision = max(0, min(1, precision))
        recall = max(0, min(1, recall))

        # Calculate F1
        if precision + recall > 0:
            f1 = 2 * (precision * recall) / (precision + recall)
        else:
            f1 = 0.0

        return Success(
            ModelMetrics(
                accuracy=accuracy,
                precision=precision,
                recall=recall,
                f1_score=f1,
            )
        )

    except Exception as e:
        return Failure(f"Evaluation failed: {e}")
