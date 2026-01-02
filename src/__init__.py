"""Metaflow to Grafana integration package.

Package structure (semantic boundaries):

    src/
    ├── domain/         # Domain models (TrainingData, ModelMetrics, etc.)
    ├── data/           # Data operations (load, validate, preprocess)
    ├── training/       # ML operations (train, evaluate)
    ├── pipeline/       # Pipeline composition with Returns
    ├── flows/          # Metaflow flow definitions
    ├── metrics.py      # Prometheus metrics collection
    └── grafana_manager.py  # Grafana dashboard management
"""
