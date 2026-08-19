import pandas as pd

from data_utils import (
    calculate_numeric_profile,
    interpret_numeric_profile,
)

def test_constant_column_profile():
    df = pd.DataFrame({
        "Constant": [100, 100, 100, 100, 100]
    })

    profile = calculate_numeric_profile(
        df,
        "Constant"
    )

    assert profile["mean"] == 100.0
    assert profile["std_dev"] == 0.0
    assert profile["coefficient_of_variation"] == 0.0
    assert profile["outliers"]["outlier_count"] == 0

    insights = interpret_numeric_profile(profile)

    assert insights == [
        "All valid values are identical, so the column has no variability."
    ]


def test_all_zero_column_profile():
    df = pd.DataFrame({
        "AllZero": [0, 0, 0, 0, 0]
    })

    profile = calculate_numeric_profile(
        df,
        "AllZero"
    )

    assert profile["mean"] == 0.0
    assert profile["std_dev"] == 0.0
    assert profile["coefficient_of_variation"] is None

    insights = interpret_numeric_profile(profile)

    assert insights == [
        "All valid values are identical, so the column has no variability."
    ]


def test_negative_values_disable_cv():
    df = pd.DataFrame({
        "NegativeValues": [-100, -80, -60, -40, -20]
    })

    profile = calculate_numeric_profile(
        df,
        "NegativeValues"
    )

    assert profile["mean"] == -60.0
    assert profile["coefficient_of_variation"] is None
    assert profile["skewness"] == 0.0


def test_mostly_missing_column_tracks_coverage():
    df = pd.DataFrame({
        "MostlyMissing": [
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            10,
            20,
            30,
        ]
    })

    profile = calculate_numeric_profile(
        df,
        "MostlyMissing"
    )

    assert profile["count"] == 3
    assert profile["missing"] == 7
    assert profile["coverage_percentage"] == 30.0
    assert profile["outliers"] is None

    insights = interpret_numeric_profile(profile)

    assert any(
        "30.00%" in insight
        for insight in insights
    )


def test_tiny_sample_warns_user():
    df = pd.DataFrame({
        "TinySample": [10, 20]
    })

    profile = calculate_numeric_profile(
        df,
        "TinySample"
    )

    assert profile["count"] == 2
    assert profile["skewness"] is None
    assert profile["outliers"] is None

    insights = interpret_numeric_profile(profile)

    assert any(
        "Only **2 valid records**" in insight
        for insight in insights
    )


def test_mixed_numeric_column_tracks_unusable_values():
    df = pd.DataFrame({
        "MixedNumeric": [
            "10",
            "20",
            "30",
            "N/A",
            "40",
            "not available",
            "50",
        ]
    })

    profile = calculate_numeric_profile(
        df,
        "MixedNumeric"
    )

    assert profile["count"] == 5
    assert profile["missing"] == 0
    assert profile["unusable_count"] == 2
    assert round(
        profile["coverage_percentage"],
        2
    ) == 71.43

    insights = interpret_numeric_profile(profile)

    assert any(
        "2 values" in insight
        for insight in insights
    )


def test_extreme_values_do_not_overflow():
    df = pd.DataFrame({
        "ExtremeValues": [
            1e3,
            1e6,
            1e9,
            1e12,
            1e15,
        ]
    })

    profile = calculate_numeric_profile(
        df,
        "ExtremeValues"
    )

    assert profile is not None
    assert profile["mean"] is not None
    assert profile["std_dev"] is not None
    assert profile["skewness"] is not None
    assert profile["outliers"] is not None