"""Data loading functionality."""

import random
import time

from returns.result import Failure, Result, Success

from src.domain import PipelineConfig, TrainingData


def load_data(config: PipelineConfig) -> Result[TrainingData, str]:
    """Load training data based on configuration.

    Args:
        config: Pipeline configuration with data parameters.

    Returns:
        Success with TrainingData or Failure with error message.
    """
    try:
        # Simulate I/O latency
        time.sleep(random.uniform(0.1, 0.3))

        samples = config.samples
        features = config.features

        if samples <= 0:
            return Failure(f"Invalid sample count: {samples} (must be positive)")

        if features <= 0:
            return Failure(f"Invalid feature count: {features} (must be positive)")

        return Success(
            TrainingData(
                samples=samples,
                features=features,
                is_validated=False,
                is_preprocessed=False,
            )
        )

    except Exception as e:
        return Failure(f"Data loading failed: {e}")
