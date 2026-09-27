"""
Metrics aggregation and reporting.
"""
from typing import Dict, List, Optional

import numpy as np
import pandas as pd

from .core import (
    EvaluationMetrics,
    MetricResult,
    calculate_accuracy,
    calculate_automation_coverage_curve,
    calculate_baseline_accuracy,
    calculate_brier_score,
    calculate_ece,
    calculate_latency_percentiles,
    calculate_macro_f1,
    calculate_ordinal_mae,
    calculate_random_baseline_accuracy,
)


def compute_choice_metrics(
    predictions: List[str],
    labels: List[str],
    confidences: List[float],
    probabilities: Optional[Dict[str, List[Dict[str, float]]]] = None,
    latencies_ms: Optional[List[float]] = None,
    costs_usd: Optional[List[float]] = None,
) -> EvaluationMetrics:
    """
    Compute comprehensive metrics for choice questions.
    
    Args:
        predictions: Predicted choices
        labels: True labels
        confidences: Confidence scores
        probabilities: Per-class probabilities (optional)
        latencies_ms: Latency per prediction
        costs_usd: Cost per prediction
    
    Returns:
        Complete evaluation metrics
    """
    n = len(predictions)
    
    # Quality metrics
    accuracy = calculate_accuracy(predictions, labels, bootstrap=True)
    macro_f1 = calculate_macro_f1(predictions, labels, bootstrap=True)
    
    # Calibration metrics
    correct = [pred == label for pred, label in zip(predictions, labels)]
    brier = calculate_brier_score(confidences, correct)
    
    # ECE requires per-class probabilities
    if probabilities:
        # For simplicity, use confidence as proxy
        ece = calculate_ece(confidences, correct, correct)
    else:
        ece = MetricResult(value=0, label="ece")
    
    # Performance metrics
    if latencies_ms:
        p50, p95, p99 = calculate_latency_percentiles(latencies_ms)
        total_time_sec = sum(latencies_ms) / 1000
        throughput = n / total_time_sec if total_time_sec > 0 else 0
    else:
        p50 = p95 = p99 = throughput = 0
    
    if costs_usd:
        cost_per_1000 = (sum(costs_usd) / n) * 1000 if n > 0 else 0
    else:
        cost_per_1000 = 0
    
    # Business metrics
    low_conf_threshold = 0.7
    low_confidence_rate = sum(c < low_conf_threshold for c in confidences) / n
    
    automation_curve = calculate_automation_coverage_curve(confidences, correct)
    
    return EvaluationMetrics(
        accuracy=accuracy,
        macro_f1=macro_f1,
        brier_score=brier,
        ece=ece,
        latency_p50=p50,
        latency_p95=p95,
        latency_p99=p99,
        throughput_per_sec=throughput,
        cost_per_1000=cost_per_1000,
        low_confidence_rate=low_confidence_rate,
        automation_coverage=automation_curve,
        total_samples=n,
    )


def compute_score_metrics(
    predictions: List[int],
    labels: List[int],
    confidences: Optional[List[float]] = None,
    latencies_ms: Optional[List[float]] = None,
) -> Dict[str, float]:
    """
    Compute metrics for score (ordinal) questions.
    
    Returns:
        Dictionary of metric name -> value
    """
    mae = calculate_ordinal_mae(predictions, labels)
    
    # Treat as classification for accuracy
    acc = calculate_accuracy(
        [str(p) for p in predictions],
        [str(l) for l in labels],
        bootstrap=False,
    )
    
    metrics = {
        "ordinal_mae": mae.value,
        "exact_match_accuracy": acc.value,
    }
    
    if latencies_ms:
        p50, p95, p99 = calculate_latency_percentiles(latencies_ms)
        metrics.update({
            "latency_p50": p50,
            "latency_p95": p95,
            "latency_p99": p99,
        })
    
    return metrics


def compute_noul_metrics(
    probabilities: List[float],
    labels: List[int],
    latencies_ms: Optional[List[float]] = None,
) -> Dict[str, float]:
    """
    Compute metrics for noul (yes/no probability) questions.
    
    Returns:
        Dictionary of metric name -> value
    """
    brier = calculate_brier_score(probabilities, labels)
    
    # Convert to binary predictions at 0.5 threshold
    predictions = [1 if p >= 0.5 else 0 for p in probabilities]
    acc = calculate_accuracy(
        [str(p) for p in predictions],
        [str(l) for l in labels],
        bootstrap=False,
    )
    
    metrics = {
        "brier_score": brier.value,
        "accuracy": acc.value,
    }
    
    if latencies_ms:
        p50, p95, p99 = calculate_latency_percentiles(latencies_ms)
        metrics.update({
            "latency_p50": p50,
            "latency_p95": p95,
            "latency_p99": p99,
        })
    
    return metrics


def create_metrics_summary(metrics: EvaluationMetrics) -> pd.DataFrame:
    """Create a summary DataFrame of metrics."""
    data = {
        "Metric": [],
        "Value": [],
        "CI Lower": [],
        "CI Upper": [],
    }
    
    # Quality
    data["Metric"].append("Accuracy")
    data["Value"].append(metrics.accuracy.value)
    data["CI Lower"].append(metrics.accuracy.ci_lower or np.nan)
    data["CI Upper"].append(metrics.accuracy.ci_upper or np.nan)
    
    data["Metric"].append("Macro F1")
    data["Value"].append(metrics.macro_f1.value)
    data["CI Lower"].append(metrics.macro_f1.ci_lower or np.nan)
    data["CI Upper"].append(metrics.macro_f1.ci_upper or np.nan)
    
    # Calibration
    data["Metric"].append("Brier Score")
    data["Value"].append(metrics.brier_score.value)
    data["CI Lower"].append(np.nan)
    data["CI Upper"].append(np.nan)
    
    data["Metric"].append("ECE")
    data["Value"].append(metrics.ece.value)
    data["CI Lower"].append(np.nan)
    data["CI Upper"].append(np.nan)
    
    # Performance
    data["Metric"].append("Latency P50 (ms)")
    data["Value"].append(metrics.latency_p50)
    data["CI Lower"].append(np.nan)
    data["CI Upper"].append(np.nan)
    
    data["Metric"].append("Latency P95 (ms)")
    data["Value"].append(metrics.latency_p95)
    data["CI Lower"].append(np.nan)
    data["CI Upper"].append(np.nan)
    
    data["Metric"].append("Cost per 1000")
    data["Value"].append(metrics.cost_per_1000)
    data["CI Lower"].append(np.nan)
    data["CI Upper"].append(np.nan)
    
    return pd.DataFrame(data)
