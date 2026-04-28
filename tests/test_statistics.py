"""
Tests for statistical calculations in utils.summarize_with_ci().
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
import scipy.stats as stats

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils import summarize_with_ci


@pytest.fixture
def statistics_test_data():
    """Load test data for statistics calculations."""
    test_data_path = (
        Path(__file__).parent / "test_data" / "input" / "test_statistics.csv"
    )
    df = pd.read_csv(test_data_path)
    return df


class TestSummarizeWithCI:
    """Test the summarize_with_ci() function for statistical calculations."""

    def test_mean_calculation(self, statistics_test_data):
        """Test that mean values are calculated correctly."""
        result_df = summarize_with_ci(
            statistics_test_data,
            group_cols=["Site", "Period"],
            value_cols=["Metric1", "Metric2", "Metric3"],
        )

        # Test Site A: Metric1 values are 62.5 and 37.5
        # Mean = (62.5 + 37.5) / 2 = 50.0
        site_a_result = result_df[result_df["Site"] == "Test Site A"]
        assert len(site_a_result) == 1
        assert abs(site_a_result.iloc[0]["Metric1"] - 50.0) < 0.1

        # Test Site B: Metric1 value is 41.67
        # Mean = 41.67
        site_b_result = result_df[result_df["Site"] == "Test Site B"]
        assert len(site_b_result) == 1
        assert abs(site_b_result.iloc[0]["Metric1"] - 41.67) < 0.1

    def test_sample_size_calculation(self, statistics_test_data):
        """Test that sample size (N) is calculated correctly."""
        result_df = summarize_with_ci(
            statistics_test_data, group_cols=["Site", "Period"], value_cols=["Metric1"]
        )

        # Test Site A has 2 observations
        site_a_result = result_df[result_df["Site"] == "Test Site A"]
        assert site_a_result.iloc[0]["Metric1_N"] == 2

        # Test Site B has 1 observation
        site_b_result = result_df[result_df["Site"] == "Test Site B"]
        assert site_b_result.iloc[0]["Metric1_N"] == 1

    def test_standard_deviation_calculation(self, statistics_test_data):
        """Test that standard deviation is calculated correctly."""
        result_df = summarize_with_ci(
            statistics_test_data, group_cols=["Site", "Period"], value_cols=["Metric1"]
        )

        # Test Site A: values are 62.5 and 37.5
        # SD = sqrt(((62.5-50)^2 + (37.5-50)^2) / (2-1))
        # SD = sqrt((156.25 + 156.25) / 1) = sqrt(312.5) = 17.68
        site_a_result = result_df[result_df["Site"] == "Test Site A"]
        assert site_a_result.iloc[0]["Metric1_SD"] > 0
        assert abs(site_a_result.iloc[0]["Metric1_SD"] - 17.68) < 0.1

        # Test Site B has 1 observation, so SD should be NaN
        site_b_result = result_df[result_df["Site"] == "Test Site B"]
        assert np.isnan(site_b_result.iloc[0]["Metric1_SD"])

    def test_standard_error_calculation(self, statistics_test_data):
        """Test that standard error is calculated correctly."""
        result_df = summarize_with_ci(
            statistics_test_data, group_cols=["Site", "Period"], value_cols=["Metric1"]
        )

        # Test Site A: SE = SD / sqrt(N) = 17.68 / sqrt(2) = 12.5
        site_a_result = result_df[result_df["Site"] == "Test Site A"]
        expected_se = site_a_result.iloc[0]["Metric1_SD"] / (2**0.5)
        assert abs(site_a_result.iloc[0]["Metric1_SE"] - expected_se) < 0.1
        assert abs(site_a_result.iloc[0]["Metric1_SE"] - 12.5) < 0.1

        # Test Site B: SE with 1 sample should be NaN
        site_b_result = result_df[result_df["Site"] == "Test Site B"]
        assert np.isnan(site_b_result.iloc[0]["Metric1_SE"])

    def test_confidence_interval_calculation(self, statistics_test_data):
        """Test that confidence intervals are calculated correctly."""
        result_df = summarize_with_ci(
            statistics_test_data, group_cols=["Site", "Period"], value_cols=["Metric1"]
        )

        # Check that CI columns exist
        assert "Metric1_CI_low" in result_df.columns
        assert "Metric1_CI_high" in result_df.columns

        # Test Site A: CI should be non-NaN and straddle the mean
        site_a_result = result_df[result_df["Site"] == "Test Site A"]
        assert not pd.isna(site_a_result.iloc[0]["Metric1_CI_low"])
        assert not pd.isna(site_a_result.iloc[0]["Metric1_CI_high"])

        # CI_low should be less than or equal to mean
        assert (
            site_a_result.iloc[0]["Metric1_CI_low"] <= site_a_result.iloc[0]["Metric1"]
        )
        # CI_high should be greater than or equal to mean
        assert (
            site_a_result.iloc[0]["Metric1_CI_high"] >= site_a_result.iloc[0]["Metric1"]
        )

        # Verify exact CI values for Site A
        # Mean = 50.0, SE = 12.5, df = 1, t-critical (95%) ≈ 12.706
        # CI = mean ± t * SE = 50 ± 12.706 * 12.5 = 50 ± 158.825
        # CI_low = -108.825 (bounded to 0), CI_high = 208.825 (not bounded)
        mean = site_a_result.iloc[0]["Metric1"]
        se = site_a_result.iloc[0]["Metric1_SE"]
        n = site_a_result.iloc[0]["Metric1_N"]
        t_critical = stats.t.ppf(0.975, df=n - 1)  # 95% CI, two-tailed
        expected_ci_low = max(0, mean - t_critical * se)  # Bounded to 0
        expected_ci_high = mean + t_critical * se  # Not bounded

        assert abs(site_a_result.iloc[0]["Metric1_CI_low"] - expected_ci_low) < 0.1
        assert abs(site_a_result.iloc[0]["Metric1_CI_high"] - expected_ci_high) < 0.1

        # Test Site B: CI with 1 sample should be NaN
        site_b_result = result_df[result_df["Site"] == "Test Site B"]
        assert np.isnan(site_b_result.iloc[0]["Metric1_CI_low"])
        assert np.isnan(site_b_result.iloc[0]["Metric1_CI_high"])

    def test_error_bar_calculation(self, statistics_test_data):
        """Test that error bars (EB) are calculated correctly.

        Error bars represent mean ± SE (standard error), which is simpler than
        confidence intervals and represents approximately 68% confidence.
        """
        result_df = summarize_with_ci(
            statistics_test_data, group_cols=["Site", "Period"], value_cols=["Metric1"]
        )

        # Check that EB columns exist
        assert "Metric1_EB_low" in result_df.columns
        assert "Metric1_EB_high" in result_df.columns

        # Test Site A: EB should be mean ± SE
        site_a_result = result_df[result_df["Site"] == "Test Site A"]
        mean = site_a_result.iloc[0]["Metric1"]
        se = site_a_result.iloc[0]["Metric1_SE"]

        expected_eb_low = max(0, mean - se)  # Bounded to 0
        expected_eb_high = mean + se  # Not bounded

        assert abs(site_a_result.iloc[0]["Metric1_EB_low"] - expected_eb_low) < 0.1
        assert abs(site_a_result.iloc[0]["Metric1_EB_high"] - expected_eb_high) < 0.1

        # Test Site B: EB with 1 sample should be NaN
        site_b_result = result_df[result_df["Site"] == "Test Site B"]
        assert np.isnan(site_b_result.iloc[0]["Metric1_EB_low"])
        assert np.isnan(site_b_result.iloc[0]["Metric1_EB_high"])

    def test_all_value_columns_have_statistics(self, statistics_test_data):
        """Test that all value columns have complete statistical columns."""
        result_df = summarize_with_ci(
            statistics_test_data,
            group_cols=["Site", "Period"],
            value_cols=["Metric1", "Metric2", "Metric3"],
        )

        # All value columns should have statistical suffixes
        metrics = ["Metric1", "Metric2", "Metric3"]
        stat_suffixes = [
            "_N",
            "_SD",
            "_SE",
            "_CI_low",
            "_CI_high",
            "_EB_low",
            "_EB_high",
        ]

        for metric in metrics:
            assert metric in result_df.columns, f"Missing base metric: {metric}"
            for suffix in stat_suffixes:
                assert (
                    f"{metric}{suffix}" in result_df.columns
                ), f"Missing column: {metric}{suffix}"

    def test_multiple_group_columns(self, statistics_test_data):
        """Test that grouping works correctly with multiple columns."""
        result_df = summarize_with_ci(
            statistics_test_data, group_cols=["Site", "Period"], value_cols=["Metric1"]
        )

        # Should have 2 rows: one for Test Site A, one for Test Site B (both Spring 2024)
        assert len(result_df) == 2
        assert "Test Site A" in result_df["Site"].values
        assert "Test Site B" in result_df["Site"].values
        assert all(result_df["Period"] == "Spring 2024")

    def test_zero_lower_bound(self, statistics_test_data):
        """Test that CI_low and EB_low are bounded to 0."""
        result_df = summarize_with_ci(
            statistics_test_data, group_cols=["Site", "Period"], value_cols=["Metric1"]
        )

        # Test Site A has CI_low = 0 (bounded from negative value)
        site_a_result = result_df[result_df["Site"] == "Test Site A"]
        assert site_a_result.iloc[0]["Metric1_CI_low"] >= 0
        assert site_a_result.iloc[0]["Metric1_EB_low"] >= 0

    def test_custom_confidence_level(self, statistics_test_data):
        """
        Test that custom confidence intervels work correctly.

        NOTE: Checks by comparing CI to default 95% CI rather than
        checking for exact values, since other tests check the exact
        CI values for 95% confidence.
        """
        # Test with 90% confidence interval
        result_df_90 = summarize_with_ci(
            statistics_test_data,
            group_cols=["Site", "Period"],
            value_cols=["Metric1"],
            confidence=0.90,
        )

        # Test with 99% confidence interval
        result_df_99 = summarize_with_ci(
            statistics_test_data,
            group_cols=["Site", "Period"],
            value_cols=["Metric1"],
            confidence=0.99,
        )

        # 99% CI should be wider than 90% CI for the same data
        site_a_90 = result_df_90[result_df_90["Site"] == "Test Site A"].iloc[0]
        site_a_99 = result_df_99[result_df_99["Site"] == "Test Site A"].iloc[0]

        ci_width_90 = site_a_90["Metric1_CI_high"] - site_a_90["Metric1_CI_low"]
        ci_width_99 = site_a_99["Metric1_CI_high"] - site_a_99["Metric1_CI_low"]

        assert ci_width_99 > ci_width_90
