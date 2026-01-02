"""Data preprocessing functionality."""

import random
import time
from dataclasses import replace

from returns.result import Failure, Result, Success

from src.domain import TrainingData


def preprocess_data(data: TrainingData) -> Result[TrainingData, str]:
    """Preprocess training data (normalization, feature engineering, etc).

    Args:
        data: Validated training data.

    Returns:
        Success with preprocessed TrainingData or Failure with error message.
    """
    if not data.is_validated:
        return Failure("Cannot preprocess unvalidated data")

    try:
        # Simulate preprocessing time
        time.sleep(random.uniform(0.05, 0.15))

        # In a real scenario:
        # - Normalize features
        # - Handle missing values
        # - Feature engineering
        # - Train/test split

        return Success(
            replace(data, is_preprocessed=True)
        )

    except Exception as e:
        return Failure(f"Preprocessing failed: {e}")
