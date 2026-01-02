"""Pipeline orchestration using Returns for composition."""

from typing import Callable

from returns.result import Failure, Result, Success

from src.data import load_data, preprocess_data, validate_data
from src.domain import PipelineConfig, PipelineResult
from src.training import evaluate_model, train_model


def run_pipeline(
    config: PipelineConfig,
    on_epoch: Callable[[int, float], None] | None = None,
) -> Result[PipelineResult, str]:
    """Execute the complete ML pipeline.

    Composes all pipeline steps using Result monad for error handling.
    Each step either returns Success and continues, or returns Failure
    and short-circuits the pipeline.

    Args:
        config: Pipeline configuration.
        on_epoch: Optional callback for training progress.

    Returns:
        Success with PipelineResult or Failure with error message.
    """
    # Step 1: Load data
    data_result = load_data(config)
    if isinstance(data_result, Failure):
        return Failure(f"[Load] {data_result.failure()}")

    data = data_result.unwrap()

    # Step 2: Validate
    validated_result = validate_data(data)
    if isinstance(validated_result, Failure):
        return Failure(f"[Validate] {validated_result.failure()}")

    validated_data = validated_result.unwrap()

    # Step 3: Preprocess
    preprocessed_result = preprocess_data(validated_data)
    if isinstance(preprocessed_result, Failure):
        return Failure(f"[Preprocess] {preprocessed_result.failure()}")

    preprocessed_data = preprocessed_result.unwrap()

    # Step 4: Train
    training_result = train_model(preprocessed_data, config, on_epoch)
    if isinstance(training_result, Failure):
        return Failure(f"[Train] {training_result.failure()}")

    training = training_result.unwrap()

    # Step 5: Evaluate
    metrics_result = evaluate_model(preprocessed_data, training)
    if isinstance(metrics_result, Failure):
        return Failure(f"[Evaluate] {metrics_result.failure()}")

    metrics = metrics_result.unwrap()

    return Success(
        PipelineResult(
            data=preprocessed_data,
            training=training,
            metrics=metrics,
            success=True,
        )
    )


def run_pipeline_bind(
    config: PipelineConfig,
) -> Result[PipelineResult, str]:
    """Alternative implementation using monadic bind.

    More functional style, but requires careful state threading.
    """
    return (
        load_data(config)
        .bind(validate_data)
        .bind(preprocess_data)
        .bind(
            lambda data: train_model(data, config).map(
                lambda training: (data, training)
            )
        )
        .bind(
            lambda dt: evaluate_model(dt[0], dt[1]).map(
                lambda metrics: PipelineResult(
                    data=dt[0],
                    training=dt[1],
                    metrics=metrics,
                    success=True,
                )
            )
        )
    )
