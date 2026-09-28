"""
Metrics module for evaluation.
"""
from .aggregation import (
    compute_choice_metrics,
    compute_noul_metrics,
    compute_score_metrics,
    create_metrics_summary,
)
from .core import (
    EvaluationMetrics,
    MetricResult,
    calculate_accuracy,
    calculate_automation_coverage_curve,
    calculate_baseline_accuracy,
    calculate_brier_score,
    calculate_consistency,
    calculate_ece,
    calculate_latency_percentiles,
    calculate_macro_f1,
    calculate_ordinal_mae,
    calculate_random_baseline_accuracy,
)

__all__ = [
    "EvaluationMetrics",
    "MetricResult",
    "calculate_accuracy",
    "calculate_macro_f1",
    "calculate_brier_score",
    "calculate_ece",
    "calculate_ordinal_mae",
    "calculate_consistency",
    "calculate_latency_percentiles",
    "calculate_automation_coverage_curve",
    "calculate_baseline_accuracy",
    "calculate_random_baseline_accuracy",
    "compute_choice_metrics",
    "compute_score_metrics",
    "compute_noul_metrics",
    "create_metrics_summary",
]
