"""
Unit tests for metrics calculations.
"""
import pytest
import numpy as np

from src.metrics import (
    calculate_accuracy,
    calculate_macro_f1,
    calculate_brier_score,
    calculate_ece,
    calculate_ordinal_mae,
    calculate_consistency,
    calculate_automation_coverage_curve,
)


def test_calculate_accuracy():
    """Test accuracy calculation."""
    predictions = ["a", "b", "a", "c", "b"]
    labels = ["a", "b", "c", "c", "b"]
    
    result = calculate_accuracy(predictions, labels, bootstrap=False)
    assert result.value == 0.8  # 4 out of 5 correct: a=a, b=b, c=c, b=b
    
    # With bootstrap
    result_bootstrap = calculate_accuracy(predictions, labels, bootstrap=True, n_bootstrap=100)
    assert 0 <= result_bootstrap.value <= 1
    assert result_bootstrap.ci_lower is not None
    assert result_bootstrap.ci_upper is not None


def test_calculate_macro_f1():
    """Test macro F1 calculation."""
    predictions = ["a", "b", "a", "a", "b"]
    labels = ["a", "b", "c", "a", "b"]
    
    result = calculate_macro_f1(predictions, labels, bootstrap=False)
    assert 0 <= result.value <= 1


def test_calculate_brier_score():
    """Test Brier score calculation."""
    # Perfect predictions
    probabilities = [1.0, 1.0, 0.0, 0.0]
    labels = [1, 1, 0, 0]
    
    result = calculate_brier_score(probabilities, labels)
    assert result.value == 0.0
    
    # Worst predictions
    probabilities = [0.0, 0.0, 1.0, 1.0]
    labels = [1, 1, 0, 0]
    
    result = calculate_brier_score(probabilities, labels)
    assert result.value == 1.0


def test_calculate_ece():
    """Test ECE calculation with known values."""
    # Perfect calibration: confidence matches accuracy
    confidences = [0.9, 0.9, 0.1, 0.1]
    correct = [True, True, False, False]
    # Bin 1 [0.0-0.5]: [0.1, 0.1] with [False, False] = 0% acc, 10% conf → |0-0.1|=0.1
    # Bin 2 [0.5-1.0]: [0.9, 0.9] with [True, True] = 100% acc, 90% conf → |1-0.9|=0.1
    # ECE = 0.5 * 0.1 + 0.5 * 0.1 = 0.1
    
    result = calculate_ece(confidences, correct, n_bins=2)
    assert abs(result.value - 0.1) < 0.01
    
    # Perfect calibration with exact match
    confidences = [0.8, 0.8, 0.8, 0.8, 0.2, 0.2, 0.2, 0.2]
    correct = [True, True, True, True, False, False, False, False]
    # High bin: 80% conf, 100% acc = 20% error
    # Low bin: 20% conf, 0% acc = 20% error
    # Hmm, this isn't perfect calibration
    
    result = calculate_ece(confidences, correct, n_bins=2)
    assert 0.1 < result.value < 0.3
    
    # Poor calibration: overconfident
    confidences = [0.9, 0.9, 0.9, 0.9]
    correct = [True, False, False, False]  # 25% correct but 90% confident
    
    result = calculate_ece(confidences, correct, n_bins=2)
    # All in high bin: 25% acc, 90% conf = 65% error
    assert result.value > 0.6


def test_calculate_ordinal_mae():
    """Test ordinal MAE calculation."""
    predictions = [0, 1, 2, 1, 0]
    labels = [0, 1, 1, 2, 1]
    
    result = calculate_ordinal_mae(predictions, labels)
    assert result.value == 0.6  # (0 + 0 + 1 + 1 + 1) / 5


def test_calculate_consistency():
    """Test consistency calculation."""
    # Perfect consistency
    predictions1 = ["a", "b", "c", "a"]
    predictions2 = ["a", "b", "c", "a"]
    
    consistency = calculate_consistency(predictions1, predictions2)
    assert consistency == 1.0
    
    # No consistency
    predictions1 = ["a", "a", "a", "a"]
    predictions2 = ["b", "b", "b", "b"]
    
    consistency = calculate_consistency(predictions1, predictions2)
    assert consistency == 0.0
    
    # Partial consistency
    predictions1 = ["a", "b", "c", "a"]
    predictions2 = ["a", "b", "d", "b"]
    
    consistency = calculate_consistency(predictions1, predictions2)
    assert consistency == 0.5


def test_calculate_automation_coverage_curve():
    """Test automation coverage curve."""
    confidences = [0.9, 0.8, 0.7, 0.6, 0.5, 0.4]
    correct = [True, True, False, True, False, False]
    
    curve = calculate_automation_coverage_curve(
        confidences,
        correct,
        thresholds=[0.5, 0.7, 0.9]
    )
    
    # At threshold 0.5, 5 out of 6 samples included (0.4 is below threshold)
    assert abs(curve[0.5][0] - 5/6) < 0.01  # coverage ≈ 0.833
    assert curve[0.5][1] == 0.6  # precision (3 correct out of 5)
    
    # At threshold 0.9, only first sample
    assert curve[0.9][0] == 1/6  # coverage
    assert curve[0.9][1] == 1.0  # precision


def test_edge_cases():
    """Test edge cases."""
    # Empty inputs
    with pytest.raises(Exception):
        calculate_accuracy([], [])
    
    # Mismatched lengths
    with pytest.raises(Exception):
        calculate_consistency(["a", "b"], ["a"])
