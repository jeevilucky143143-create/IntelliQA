import pytest
from core.evaluator import compute_exact_match, compute_precision_recall_f1

def test_exact_match():
    assert compute_exact_match("Guido van Rossum", "Guido van Rossum") is True
    assert compute_exact_match("python was created by guido van rossum", "Guido van Rossum") is True

def test_precision_recall_f1():
    pred = "Guido van Rossum created Python"
    exp = "Guido van Rossum"

    res = compute_precision_recall_f1(pred, exp)
    assert res['recall'] == 1.0  # All tokens of expected are present in predicted
    assert res['precision'] > 0.0
    assert res['f1'] > 0.0
