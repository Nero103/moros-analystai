import pandas as pd
import pytest

from data_utils import (
    calculate_skewness,
    calculate_iqr_outliers,
    calculate_coefficient_of_variation,
    calculate_correlation,
    calculate_covariance,
)

def test_skewness_directions():
    df = pd.DataFrame({
        "Symmetric": [1, 2, 3, 4, 5],
        "RightSkewed": [1, 1, 1, 2, 10],
        "LeftSkewed": [-10, -2, -1, -1, -1],
    })

    symmetric = calculate_skewness(
        df,
        "Symmetric"
    )

    right = calculate_skewness(
        df,
        "RightSkewed"
    )

    left = calculate_skewness(
        df,
        "LeftSkewed"
    )

    assert symmetric == pytest.approx(0.0)
    assert right > 0
    assert left < 0


def test_skewness_rejects_nonnumeric_and_missing_columns():
    df = pd.DataFrame({
        "Category": ["A", "B", "C", "D"]
    })

    assert calculate_skewness(
        df,
        "Category"
    ) is None

    assert calculate_skewness(
        df,
        "NotAColumn"
    ) is None


def test_iqr_outlier_detection():
    df = pd.DataFrame({
        "Values": [
            10, 11, 12, 13, 14,
            15, 16, 17, 18, 100
        ]
    })

    result = calculate_iqr_outliers(
        df,
        "Values"
    )

    assert result is not None
    assert result["outlier_count"] == 1
    assert result["outlier_percentage"] == pytest.approx(
        10.0
    )


def test_iqr_no_outliers():
    df = pd.DataFrame({
        "Values": [
            10, 11, 12, 13, 14,
            15, 16, 17, 18, 19
        ]
    })

    result = calculate_iqr_outliers(
        df,
        "Values"
    )

    assert result is not None
    assert result["outlier_count"] == 0
    assert result["outlier_percentage"] == 0.0


def test_coefficient_of_variation():
    df = pd.DataFrame({
        "Values": [90, 95, 100, 105, 110]
    })

    result = calculate_coefficient_of_variation(
        df,
        "Values"
    )

    assert result == pytest.approx(
        0.0790569415
    )


def test_cv_rejects_zero_or_negative_mean():
    df = pd.DataFrame({
        "ZeroMean": [-2, -1, 0, 1, 2],
        "NegativeMean": [-100, -80, -60, -40, -20],
    })

    assert calculate_coefficient_of_variation(
        df,
        "ZeroMean"
    ) is None

    assert calculate_coefficient_of_variation(
        df,
        "NegativeMean"
    ) is None


def test_positive_and_negative_correlation():
    df = pd.DataFrame({
        "X": [1, 2, 3, 4, 5],
        "Positive": [10, 20, 30, 40, 50],
        "Negative": [50, 40, 30, 20, 10],
    })

    positive = calculate_correlation(
        df,
        "X",
        "Positive"
    )

    negative = calculate_correlation(
        df,
        "X",
        "Negative"
    )

    assert positive == pytest.approx(1.0)
    assert negative == pytest.approx(-1.0)


def test_positive_and_negative_covariance():
    df = pd.DataFrame({
        "Advertising": [10, 20, 30, 40, 50],
        "Sales": [100, 200, 300, 400, 500],
        "Inverse": [500, 400, 300, 200, 100],
    })

    positive = calculate_covariance(
        df,
        "Advertising",
        "Sales"
    )

    negative = calculate_covariance(
        df,
        "Advertising",
        "Inverse"
    )

    assert positive == pytest.approx(2500.0)
    assert negative == pytest.approx(-2500.0)