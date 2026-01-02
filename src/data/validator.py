"""Data validation functionality."""

from dataclasses import replace

from returns.result import Failure, Result, Success

from src.domain import TrainingData

# Validation thresholds
MIN_SAMPLES = 100
MIN_FEATURES = 1
MAX_FEATURES = 10000


def validate_data(data: TrainingData) -> Result[TrainingData, str]:
    """Validate training data meets minimum requirements.

    Args:
        data: Training data to validate.

    Returns:
        Success with validated TrainingData or Failure with error message.
    """
    errors: list[str] = []

    if data.samples < MIN_SAMPLES:
        errors.append(f"Insufficient samples: {data.samples} < {MIN_SAMPLES} minimum")

    if data.features < MIN_FEATURES:
        errors.append(f"Invalid features: {data.features} < {MIN_FEATURES} minimum")

    if data.features > MAX_FEATURES:
        errors.append(f"Too many features: {data.features} > {MAX_FEATURES} maximum")

    if errors:
        return Failure("; ".join(errors))

    # Return new instance with is_validated=True (immutable pattern)
    return Success(
        replace(data, is_validated=True)
    )
