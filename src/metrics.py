"""Metrics collector for pushing Metaflow metrics to Prometheus Pushgateway."""

import os
import time
from functools import wraps
from typing import Any, Callable

from prometheus_client import CollectorRegistry, Counter, Gauge, Histogram, push_to_gateway


class MetaflowMetrics:
    """Prometheus metrics collector for Metaflow pipelines."""

    def __init__(
        self,
        pushgateway_url: str = "localhost:9091",
        job_name: str = "metaflow",
    ):
        self.pushgateway_url = pushgateway_url
        self.job_name = job_name
        self.registry = CollectorRegistry()

        # Flow-level metrics
        self.flow_runs_total = Counter(
            "metaflow_flow_runs_total",
            "Total number of flow runs",
            ["flow_name", "status"],
            registry=self.registry,
        )

        self.flow_run_duration_seconds = Histogram(
            "metaflow_flow_run_duration_seconds",
            "Duration of flow runs in seconds",
            ["flow_name"],
            buckets=[1, 5, 10, 30, 60, 120, 300, 600, 1800, 3600],
            registry=self.registry,
        )

        # Step-level metrics
        self.step_runs_total = Counter(
            "metaflow_step_runs_total",
            "Total number of step runs",
            ["flow_name", "step_name", "status"],
            registry=self.registry,
        )

        self.step_duration_seconds = Histogram(
            "metaflow_step_duration_seconds",
            "Duration of steps in seconds",
            ["flow_name", "step_name"],
            buckets=[0.1, 0.5, 1, 5, 10, 30, 60, 120, 300],
            registry=self.registry,
        )

        # Task-level metrics
        self.task_count = Gauge(
            "metaflow_task_count",
            "Number of tasks per step",
            ["flow_name", "step_name"],
            registry=self.registry,
        )

        # Custom ML metrics
        self.model_accuracy = Gauge(
            "metaflow_model_accuracy",
            "Model accuracy metric",
            ["flow_name", "model_name"],
            registry=self.registry,
        )

        self.training_loss = Gauge(
            "metaflow_training_loss",
            "Training loss metric",
            ["flow_name", "step_name", "epoch"],
            registry=self.registry,
        )

        self.data_size = Gauge(
            "metaflow_data_size_bytes",
            "Size of data artifacts in bytes",
            ["flow_name", "step_name", "artifact_name"],
            registry=self.registry,
        )

    def push(self, grouping_key: dict[str, str] | None = None) -> None:
        """Push metrics to Prometheus Pushgateway."""
        push_to_gateway(
            self.pushgateway_url,
            job=self.job_name,
            registry=self.registry,
            grouping_key=grouping_key or {},
        )

    def record_flow_start(self, flow_name: str) -> float:
        """Record flow start and return start time."""
        return time.time()

    def record_flow_end(
        self,
        flow_name: str,
        start_time: float,
        status: str = "success",
    ) -> None:
        """Record flow end with duration and status."""
        duration = time.time() - start_time
        self.flow_runs_total.labels(flow_name=flow_name, status=status).inc()
        self.flow_run_duration_seconds.labels(flow_name=flow_name).observe(duration)
        self.push({"flow_name": flow_name})

    def record_step_start(self, flow_name: str, step_name: str) -> float:
        """Record step start and return start time."""
        return time.time()

    def record_step_end(
        self,
        flow_name: str,
        step_name: str,
        start_time: float,
        status: str = "success",
    ) -> None:
        """Record step end with duration and status."""
        duration = time.time() - start_time
        self.step_runs_total.labels(
            flow_name=flow_name, step_name=step_name, status=status
        ).inc()
        self.step_duration_seconds.labels(
            flow_name=flow_name, step_name=step_name
        ).observe(duration)
        self.push({"flow_name": flow_name, "step_name": step_name})

    def record_model_metrics(
        self,
        flow_name: str,
        model_name: str,
        accuracy: float,
    ) -> None:
        """Record model performance metrics."""
        self.model_accuracy.labels(flow_name=flow_name, model_name=model_name).set(
            accuracy
        )
        self.push({"flow_name": flow_name, "model_name": model_name})

    def record_training_loss(
        self,
        flow_name: str,
        step_name: str,
        epoch: int,
        loss: float,
    ) -> None:
        """Record training loss per epoch."""
        self.training_loss.labels(
            flow_name=flow_name, step_name=step_name, epoch=str(epoch)
        ).set(loss)
        self.push({"flow_name": flow_name, "step_name": step_name})


def with_metrics(
    metrics: MetaflowMetrics,
    flow_name: str,
) -> Callable:
    """Decorator to automatically track step metrics."""

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            step_name = func.__name__
            start_time = metrics.record_step_start(flow_name, step_name)
            try:
                result = func(*args, **kwargs)
                metrics.record_step_end(flow_name, step_name, start_time, "success")
                return result
            except Exception as e:
                metrics.record_step_end(flow_name, step_name, start_time, "failure")
                raise e

        return wrapper

    return decorator


# Default metrics instance
_default_metrics: MetaflowMetrics | None = None


def get_metrics() -> MetaflowMetrics:
    """Get or create default metrics instance."""
    global _default_metrics
    if _default_metrics is None:
        pushgateway_url = os.getenv("PUSHGATEWAY_URL", "localhost:9091")
        _default_metrics = MetaflowMetrics(pushgateway_url=pushgateway_url)
    return _default_metrics
