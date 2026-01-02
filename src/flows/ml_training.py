"""ML Training Flow - Metaflow orchestration layer.

This flow delegates all business logic to the pipeline module,
acting purely as an orchestrator that:
- Manages step execution order
- Handles success/failure branching
- Records metrics to Grafana/Prometheus
"""

from metaflow import FlowSpec, step
from returns.result import Failure, Success

from src.domain import PipelineConfig, PipelineResult
from src.metrics import get_metrics
from src.pipeline import run_pipeline


class MLTrainingFlow(FlowSpec):
    """
    ML training flow using Returns for type-safe error handling.

    Architecture:
    - Domain layer: Pure data models (src/domain/)
    - Data layer: Load, validate, preprocess (src/data/)
    - Training layer: Train, evaluate (src/training/)
    - Pipeline layer: Composition with Result monad (src/pipeline/)
    - Flow layer: Metaflow orchestration (this file)
    """

    @step
    def start(self):
        """Initialize flow configuration and metrics."""
        self.metrics = get_metrics()
        self.flow_start_time = self.metrics.record_flow_start("MLTrainingFlow")

        # Configure pipeline
        self.config = PipelineConfig(
            samples=50000,
            features=50,
            epochs=10,
        )

        print("=" * 60)
        print("MLTrainingFlow - Starting")
        print("=" * 60)
        print(f"Config: {self.config}")

        self.next(self.run_pipeline)

    @step
    def run_pipeline(self):
        """Execute the ML pipeline."""
        step_start = self.metrics.record_step_start("MLTrainingFlow", "run_pipeline")

        def on_epoch(epoch: int, loss: float) -> None:
            """Callback for epoch progress."""
            print(f"  Epoch {epoch:2d}/{self.config.epochs} - Loss: {loss:.4f}")
            self.metrics.record_training_loss(
                flow_name="MLTrainingFlow",
                step_name="train",
                epoch=epoch,
                loss=loss,
            )

        print("\nRunning pipeline...")
        result = run_pipeline(self.config, on_epoch=on_epoch)

        match result:
            case Success(pipeline_result):
                self._store_success(pipeline_result)
                self.pipeline_success = True
                self.metrics.record_step_end(
                    "MLTrainingFlow", "run_pipeline", step_start, "success"
                )
                self.next(self.end)

            case Failure(error):
                self._store_failure(error)
                self.pipeline_success = False
                self.metrics.record_step_end(
                    "MLTrainingFlow", "run_pipeline", step_start, "failure"
                )
                self.next(self.handle_error)

    def _store_success(self, result: PipelineResult) -> None:
        """Store successful pipeline results."""
        # Data metrics
        self.data_samples = result.data.samples
        self.data_features = result.data.features

        # Training metrics
        self.training_epochs = result.training.epochs
        self.training_history = list(result.training.history)
        self.final_loss = result.training.final_loss

        # Model metrics
        self.accuracy = result.metrics.accuracy
        self.precision = result.metrics.precision
        self.recall = result.metrics.recall
        self.f1_score = result.metrics.f1_score

        # Record to Prometheus
        self.metrics.record_model_metrics(
            flow_name="MLTrainingFlow",
            model_name="ml_model",
            accuracy=self.accuracy,
        )

        print("\n" + "=" * 60)
        print("Pipeline Results")
        print("=" * 60)
        print(f"Data:     {self.data_samples} samples, {self.data_features} features")
        print(f"Training: {self.training_epochs} epochs, loss: {self.final_loss:.4f}")
        print(f"Accuracy:  {self.accuracy:.4f}")
        print(f"Precision: {self.precision:.4f}")
        print(f"Recall:    {self.recall:.4f}")
        print(f"F1 Score:  {self.f1_score:.4f}")

    def _store_failure(self, error: str) -> None:
        """Store failure information."""
        self.error_message = error
        print(f"\nPipeline failed: {error}")

    @step
    def handle_error(self):
        """Handle pipeline errors."""
        print("\n" + "=" * 60)
        print("Error Recovery")
        print("=" * 60)
        print(f"Error: {self.error_message}")
        print("Performing cleanup...")

        # In production:
        # - Send alerts
        # - Log detailed diagnostics
        # - Attempt recovery

        self.next(self.end)

    @step
    def end(self):
        """Finalize the flow."""
        print("\n" + "=" * 60)

        if self.pipeline_success:
            print(f"MLTrainingFlow completed successfully")
            print(f"Final accuracy: {self.accuracy:.4f}")
            status = "success"
        else:
            print("MLTrainingFlow completed with errors")
            status = "failure"

        print("=" * 60)

        self.metrics.record_flow_end(
            "MLTrainingFlow",
            self.flow_start_time,
            status,
        )


if __name__ == "__main__":
    MLTrainingFlow()
