"""
Metrics calculation for decision model evaluation.
"""
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

import numpy as np
from sklearn.metrics import accuracy_score, f1_score, mean_absolute_error


@dataclass
class MetricResult:
    """A single metric result with confidence interval."""
    
    value: float
    ci_lower: Optional[float] = None
    ci_upper: Optional[float] = None
    label: str = ""
    
    def __str__(self) -> str:
        if self.ci_lower is not None and self.ci_upper is not None:
            return f"{self.value:.4f} (95% CI: {self.ci_lower:.4f}-{self.ci_upper:.4f})"
        return f"{self.value:.4f}"


@dataclass
class EvaluationMetrics:
    """Complete evaluation metrics."""
    
    # Quality metrics
    accuracy: MetricResult
    macro_f1: MetricResult
    
    # Calibration metrics
    brier_score: MetricResult
    ece: MetricResult
    
    # Consistency metrics
    paraphrase_consistency: Optional[MetricResult] = None
    order_consistency: Optional[MetricResult] = None
    
    # Performance metrics
    latency_p50: float = 0
    latency_p95: float = 0
    latency_p99: float = 0
    throughput_per_sec: float = 0
    cost_per_1000: float = 0
    
    # Business metrics
    low_confidence_rate: float = 0
    automation_coverage: Optional[Dict[float, float]] = None  # threshold -> coverage
    
    # Additional context
    total_samples: int = 0
    schema_validity: float = 1.0


def calculate_accuracy(
    predictions: List[str],
    labels: List[str],
    bootstrap: bool = True,
    n_bootstrap: int = 1000,
) -> MetricResult:
    """
    Calculate accuracy with optional bootstrap confidence intervals.
    
    Args:
        predictions: Predicted labels
        labels: True labels
        bootstrap: Whether to compute bootstrap CI
        n_bootstrap: Number of bootstrap iterations
    
    Returns:
        Accuracy metric with optional confidence interval
    """
    acc = accuracy_score(labels, predictions)
    
    if not bootstrap:
        return MetricResult(value=acc)
    
    # Bootstrap confidence interval
    n = len(predictions)
    bootstrap_accs = []
    
    for _ in range(n_bootstrap):
        indices = np.random.choice(n, size=n, replace=True)
        boot_preds = [predictions[i] for i in indices]
        boot_labels = [labels[i] for i in indices]
        boot_acc = accuracy_score(boot_labels, boot_preds)
        bootstrap_accs.append(boot_acc)
    
    ci_lower = np.percentile(bootstrap_accs, 2.5)
    ci_upper = np.percentile(bootstrap_accs, 97.5)
    
    return MetricResult(value=acc, ci_lower=ci_lower, ci_upper=ci_upper, label="accuracy")


def calculate_macro_f1(
    predictions: List[str],
    labels: List[str],
    bootstrap: bool = True,
    n_bootstrap: int = 1000,
) -> MetricResult:
    """Calculate macro-averaged F1 score."""
    f1 = f1_score(labels, predictions, average="macro", zero_division=0)
    
    if not bootstrap:
        return MetricResult(value=f1)
    
    n = len(predictions)
    bootstrap_f1s = []
    
    for _ in range(n_bootstrap):
        indices = np.random.choice(n, size=n, replace=True)
        boot_preds = [predictions[i] for i in indices]
        boot_labels = [labels[i] for i in indices]
        boot_f1 = f1_score(boot_labels, boot_preds, average="macro", zero_division=0)
        bootstrap_f1s.append(boot_f1)
    
    ci_lower = np.percentile(bootstrap_f1s, 2.5)
    ci_upper = np.percentile(bootstrap_f1s, 97.5)
    
    return MetricResult(value=f1, ci_lower=ci_lower, ci_upper=ci_upper, label="macro_f1")


def calculate_brier_score(
    probabilities: List[float],
    labels: List[int],
) -> MetricResult:
    """
    Calculate Brier score for binary or probability predictions.
    
    Lower is better. Brier = mean((p - y)^2)
    """
    probs = np.array(probabilities)
    targets = np.array(labels)
    brier = np.mean((probs - targets) ** 2)
    return MetricResult(value=brier, label="brier_score")


def calculate_ece(
    confidences: List[float],
    correct: List[bool],
    n_bins: int = 10,
) -> MetricResult:
    """
    Calculate Expected Calibration Error (ECE).
    
    ECE measures the difference between confidence and accuracy across bins.
    
    Args:
        confidences: Confidence scores (0-1) for each prediction
        correct: Boolean array indicating if each prediction was correct
        n_bins: Number of bins for calibration (default 10)
    
    Returns:
        ECE metric result
    """
    confs = np.array(confidences)
    corr = np.array(correct, dtype=float)
    
    bin_boundaries = np.linspace(0, 1, n_bins + 1)
    ece = 0
    
    for i in range(n_bins):
        lower = bin_boundaries[i]
        upper = bin_boundaries[i + 1]
        
        in_bin = (confs >= lower) & (confs < upper)
        if i == n_bins - 1:  # Include 1.0 in last bin
            in_bin = in_bin | (confs == 1.0)
        
        if np.sum(in_bin) > 0:
            bin_accuracy = np.mean(corr[in_bin])
            bin_confidence = np.mean(confs[in_bin])
            bin_weight = np.sum(in_bin) / len(confs)
            ece += bin_weight * abs(bin_accuracy - bin_confidence)
    
    return MetricResult(value=ece, label="ece")
    
    return MetricResult(value=ece, label="ece")


def calculate_ordinal_mae(
    predictions: List[int],
    labels: List[int],
) -> MetricResult:
    """Calculate Mean Absolute Error for ordinal (score) questions."""
    mae = mean_absolute_error(labels, predictions)
    return MetricResult(value=mae, label="ordinal_mae")


def calculate_consistency(
    predictions1: List[str],
    predictions2: List[str],
) -> float:
    """
    Calculate consistency rate between two prediction sets.
    
    Used for paraphrase consistency and option-order permutation.
    """
    if len(predictions1) != len(predictions2):
        raise ValueError("Prediction lists must have same length")
    
    matches = sum(p1 == p2 for p1, p2 in zip(predictions1, predictions2))
    return matches / len(predictions1)


def calculate_latency_percentiles(
    latencies_ms: List[float],
) -> Tuple[float, float, float]:
    """Calculate latency percentiles (p50, p95, p99)."""
    if not latencies_ms:
        return 0, 0, 0
    
    p50 = np.percentile(latencies_ms, 50)
    p95 = np.percentile(latencies_ms, 95)
    p99 = np.percentile(latencies_ms, 99)
    
    return p50, p95, p99


def calculate_automation_coverage_curve(
    confidences: List[float],
    correct: List[bool],
    thresholds: Optional[List[float]] = None,
) -> Dict[float, Tuple[float, float]]:
    """
    Calculate automation coverage-precision curve.
    
    For each confidence threshold, compute:
    - Coverage: % of samples that meet threshold
    - Precision: accuracy among samples meeting threshold
    
    Args:
        confidences: Confidence scores
        correct: Whether each prediction was correct
        thresholds: Confidence thresholds to evaluate (default: 0.5, 0.6, ..., 0.95)
    
    Returns:
        Dict mapping threshold -> (coverage, precision)
    """
    if thresholds is None:
        thresholds = [0.5, 0.6, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95]
    
    confs = np.array(confidences)
    corr = np.array(correct)
    
    curve = {}
    for threshold in thresholds:
        above_threshold = confs >= threshold
        coverage = np.mean(above_threshold)
        
        if np.sum(above_threshold) > 0:
            precision = np.mean(corr[above_threshold])
        else:
            precision = 0
        
        curve[threshold] = (coverage, precision)
    
    return curve


def calculate_baseline_accuracy(labels: List[str]) -> float:
    """Calculate majority class baseline accuracy."""
    if not labels:
        return 0
    
    unique, counts = np.unique(labels, return_counts=True)
    majority_count = np.max(counts)
    return majority_count / len(labels)


def calculate_random_baseline_accuracy(labels: List[str]) -> float:
    """Calculate random baseline accuracy (1 / num_classes)."""
    if not labels:
        return 0
    
    num_classes = len(set(labels))
    return 1.0 / num_classes if num_classes > 0 else 0
