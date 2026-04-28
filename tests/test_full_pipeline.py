"""
Integration tests for full pipeline metrics calculations.
"""

import sys
from pathlib import Path

import pandas as pd
import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from fish_metrics import calculate_fish_metrics
from invert_metrics import calculate_inverts_metrics
from subs_metrics import calculate_subs_metrics


class TestFishMetricsFullPipeline:
    """Integration tests for fish metrics pipeline."""

    def test_calculate_fish_metrics_runs(
        self, preprocessed_fish_data, fish_dive_numbers, redirect_constants_to_test_data
    ):
        """Test that the main fish metrics function runs without errors."""
        result_df = calculate_fish_metrics(
            preprocessed_fish_data, fish_dive_numbers, "seasonal"
        )

        # Check that result has expected structure
        assert isinstance(result_df, pd.DataFrame)
        assert "Site" in result_df.columns
        assert "Period" in result_df.columns

        # Check all the expected columns exist
        base_metrics = [
            "Corallivore Density",
            "Detritivore Density",
            "Omnivore Density",
            "Carnivore Density",
            "Herbivore Density",
            "Total Density",
            "Total Biomass Density",
            "Commercial Density",
            "Commercial Biomass Density",
        ]
        stat_suffixes = [
            "_N",
            "_SD",
            "_SE",
            "_CI_low",
            "_CI_high",
            "_EB_low",
            "_EB_high",
        ]
        expected_columns = ["Period", "Site"]
        for metric in base_metrics:
            expected_columns.append(metric)
            expected_columns.extend([f"{metric}{suffix}" for suffix in stat_suffixes])
        for col in expected_columns:
            assert col in result_df.columns, f"Missing column: {col}"
        # Check no other columns exist
        assert len(result_df.columns) == len(
            expected_columns
        ), "Unexpected columns in result"

    def test_multiple_sites_handled_correctly(self, preprocessed_fish_data):
        """Test that metrics are calculated separately for each site."""
        sites = preprocessed_fish_data["Site"].unique()
        assert len(sites) == 2
        assert "Test Site A" in sites
        assert "Test Site B" in sites

    def test_no_nan_in_final_results(
        self, preprocessed_fish_data, fish_dive_numbers, redirect_constants_to_test_data
    ):
        """Test that final metrics don't contain unexpected NaN values."""
        result_df = calculate_fish_metrics(
            preprocessed_fish_data, fish_dive_numbers, "seasonal"
        )

        # Density columns should not have NaN (they're filled with 0)
        # Check base metric columns (without suffixes like _N, _SD, etc.)
        density_cols = [
            col
            for col in result_df.columns
            if "Density" in col
            and not any(suffix in col for suffix in ["_N", "_SD", "_SE", "_CI", "_EB"])
        ]
        for col in density_cols:
            assert not result_df[col].isna().any(), f"Column {col} contains NaN values"

    def test_final_output_values(
        self, preprocessed_fish_data, fish_dive_numbers, redirect_constants_to_test_data
    ):
        """Integration test: verify all final output values match expected calculations."""
        result_df = calculate_fish_metrics(
            preprocessed_fish_data, fish_dive_numbers, "seasonal"
        )

        # Test Site A: 2 surveys
        site_a = result_df[result_df["Site"] == "Test Site A"].iloc[0]

        # Total Density: survey_001=40, survey_002=27, mean=33.5
        # N=2, SD=9.19 (standard deviation), SE=6.5 (standard error)
        # t_crit=12.706 (df=1, 95% CI), CI=confidence interval, EB=error bars (mean±SE)
        assert abs(site_a["Total Density"] - 33.5) < 0.1
        assert site_a["Total Density_N"] == 2
        assert abs(site_a["Total Density_SD"] - 9.19) < 0.1
        assert abs(site_a["Total Density_SE"] - 6.5) < 0.1
        assert abs(site_a["Total Density_CI_low"] - 0.0) < 0.1
        assert abs(site_a["Total Density_CI_high"] - 116.09) < 0.1
        assert abs(site_a["Total Density_EB_low"] - 27.0) < 0.1
        assert abs(site_a["Total Density_EB_high"] - 40.0) < 0.1

        # Commercial Density: survey_001=15, survey_002=27, mean=21.0
        # N=2, SD=8.49, SE=6.0
        assert abs(site_a["Commercial Density"] - 21.0) < 0.1
        assert site_a["Commercial Density_N"] == 2
        assert abs(site_a["Commercial Density_SD"] - 8.49) < 0.1
        assert abs(site_a["Commercial Density_SE"] - 6.0) < 0.1
        assert abs(site_a["Commercial Density_CI_low"] - 0.0) < 0.1
        assert abs(site_a["Commercial Density_CI_high"] - 97.24) < 0.1
        assert abs(site_a["Commercial Density_EB_low"] - 15.0) < 0.1
        assert abs(site_a["Commercial Density_EB_high"] - 27.0) < 0.1

        # Herbivore Density: survey_001=10, survey_002=23, mean=16.5
        # N=2, SD=9.19, SE=6.5
        assert abs(site_a["Herbivore Density"] - 16.5) < 0.1
        assert site_a["Herbivore Density_N"] == 2
        assert abs(site_a["Herbivore Density_SD"] - 9.19) < 0.1
        assert abs(site_a["Herbivore Density_SE"] - 6.5) < 0.1
        assert abs(site_a["Herbivore Density_CI_low"] - 0.0) < 0.1
        assert abs(site_a["Herbivore Density_CI_high"] - 99.09) < 0.1
        assert abs(site_a["Herbivore Density_EB_low"] - 10.0) < 0.1
        assert abs(site_a["Herbivore Density_EB_high"] - 23.0) < 0.1

        # Carnivore Density: survey_001=2, survey_002=0, mean=1.0
        # N=2, SD=1.41, SE=1.0
        assert abs(site_a["Carnivore Density"] - 1.0) < 0.1
        assert site_a["Carnivore Density_N"] == 2
        assert abs(site_a["Carnivore Density_SD"] - 1.41) < 0.1
        assert abs(site_a["Carnivore Density_SE"] - 1.0) < 0.1
        assert abs(site_a["Carnivore Density_CI_low"] - 0.0) < 0.1
        assert abs(site_a["Carnivore Density_CI_high"] - 13.71) < 0.1
        assert abs(site_a["Carnivore Density_EB_low"] - 0.0) < 0.1
        assert abs(site_a["Carnivore Density_EB_high"] - 2.0) < 0.1

        # Omnivore Density: survey_001=5, survey_002=4, mean=4.5
        # N=2, SD=0.71, SE=0.5
        assert abs(site_a["Omnivore Density"] - 4.5) < 0.1
        assert site_a["Omnivore Density_N"] == 2
        assert abs(site_a["Omnivore Density_SD"] - 0.71) < 0.1
        assert abs(site_a["Omnivore Density_SE"] - 0.5) < 0.1
        assert abs(site_a["Omnivore Density_CI_low"] - 0.0) < 0.1
        assert abs(site_a["Omnivore Density_CI_high"] - 10.85) < 0.1
        assert abs(site_a["Omnivore Density_EB_low"] - 4.0) < 0.1
        assert abs(site_a["Omnivore Density_EB_high"] - 5.0) < 0.1

        # Detritivore Density: survey_001=3, survey_002=0, mean=1.5
        # N=2, SD=2.12, SE=1.5
        assert abs(site_a["Detritivore Density"] - 1.5) < 0.1
        assert site_a["Detritivore Density_N"] == 2
        assert abs(site_a["Detritivore Density_SD"] - 2.12) < 0.1
        assert abs(site_a["Detritivore Density_SE"] - 1.5) < 0.1
        assert abs(site_a["Detritivore Density_CI_low"] - 0.0) < 0.1
        assert abs(site_a["Detritivore Density_CI_high"] - 20.56) < 0.1
        assert abs(site_a["Detritivore Density_EB_low"] - 0.0) < 0.1
        assert abs(site_a["Detritivore Density_EB_high"] - 3.0) < 0.1

        # Corallivore Density: survey_001=20, survey_002=0, mean=10.0
        # N=2, SD=14.14, SE=10.0
        assert abs(site_a["Corallivore Density"] - 10.0) < 0.1
        assert site_a["Corallivore Density_N"] == 2
        assert abs(site_a["Corallivore Density_SD"] - 14.14) < 0.1
        assert abs(site_a["Corallivore Density_SE"] - 10.0) < 0.1
        assert abs(site_a["Corallivore Density_CI_low"] - 0.0) < 0.1
        assert abs(site_a["Corallivore Density_CI_high"] - 137.06) < 0.1
        assert abs(site_a["Corallivore Density_EB_low"] - 0.0) < 0.1
        assert abs(site_a["Corallivore Density_EB_high"] - 20.0) < 0.1

        # Test Site B: 1 survey (all SD/SE/CI/EB should be NaN)
        site_b = result_df[result_df["Site"] == "Test Site B"].iloc[0]

        # Total Density: survey_003=34
        assert abs(site_b["Total Density"] - 34.0) < 0.1
        assert site_b["Total Density_N"] == 1
        assert np.isnan(site_b["Total Density_SD"])
        assert np.isnan(site_b["Total Density_SE"])
        assert np.isnan(site_b["Total Density_CI_low"])
        assert np.isnan(site_b["Total Density_CI_high"])
        assert np.isnan(site_b["Total Density_EB_low"])
        assert np.isnan(site_b["Total Density_EB_high"])

        # Commercial Density: survey_003=6 (Parrotfish only)
        assert abs(site_b["Commercial Density"] - 6.0) < 0.1
        assert site_b["Commercial Density_N"] == 1
        assert np.isnan(site_b["Commercial Density_SD"])
        assert np.isnan(site_b["Commercial Density_SE"])
        assert np.isnan(site_b["Commercial Density_CI_low"])
        assert np.isnan(site_b["Commercial Density_CI_high"])
        assert np.isnan(site_b["Commercial Density_EB_low"])
        assert np.isnan(site_b["Commercial Density_EB_high"])

        # Herbivore Density: survey_003=0
        assert abs(site_b["Herbivore Density"] - 0.0) < 0.1
        assert site_b["Herbivore Density_N"] == 1
        assert np.isnan(site_b["Herbivore Density_SD"])
        assert np.isnan(site_b["Herbivore Density_SE"])
        assert np.isnan(site_b["Herbivore Density_CI_low"])
        assert np.isnan(site_b["Herbivore Density_CI_high"])
        assert np.isnan(site_b["Herbivore Density_EB_low"])
        assert np.isnan(site_b["Herbivore Density_EB_high"])

        # Carnivore Density: survey_003=3 (Grouper)
        assert abs(site_b["Carnivore Density"] - 3.0) < 0.1
        assert site_b["Carnivore Density_N"] == 1
        assert np.isnan(site_b["Carnivore Density_SD"])
        assert np.isnan(site_b["Carnivore Density_SE"])
        assert np.isnan(site_b["Carnivore Density_CI_low"])
        assert np.isnan(site_b["Carnivore Density_CI_high"])
        assert np.isnan(site_b["Carnivore Density_EB_low"])
        assert np.isnan(site_b["Carnivore Density_EB_high"])

        # Omnivore Density: survey_003=6 (Parrotfish)
        assert abs(site_b["Omnivore Density"] - 6.0) < 0.1
        assert site_b["Omnivore Density_N"] == 1
        assert np.isnan(site_b["Omnivore Density_SD"])
        assert np.isnan(site_b["Omnivore Density_SE"])
        assert np.isnan(site_b["Omnivore Density_CI_low"])
        assert np.isnan(site_b["Omnivore Density_CI_high"])
        assert np.isnan(site_b["Omnivore Density_EB_low"])
        assert np.isnan(site_b["Omnivore Density_EB_high"])

        # Detritivore Density: survey_003=0
        assert abs(site_b["Detritivore Density"] - 0.0) < 0.1
        assert site_b["Detritivore Density_N"] == 1
        assert np.isnan(site_b["Detritivore Density_SD"])
        assert np.isnan(site_b["Detritivore Density_SE"])
        assert np.isnan(site_b["Detritivore Density_CI_low"])
        assert np.isnan(site_b["Detritivore Density_CI_high"])
        assert np.isnan(site_b["Detritivore Density_EB_low"])
        assert np.isnan(site_b["Detritivore Density_EB_high"])

        # Corallivore Density: survey_003=25 (Damselfish)
        assert abs(site_b["Corallivore Density"] - 25.0) < 0.1
        assert site_b["Corallivore Density_N"] == 1
        assert np.isnan(site_b["Corallivore Density_SD"])
        assert np.isnan(site_b["Corallivore Density_SE"])
        assert np.isnan(site_b["Corallivore Density_CI_low"])
        assert np.isnan(site_b["Corallivore Density_CI_high"])
        assert np.isnan(site_b["Corallivore Density_EB_low"])
        assert np.isnan(site_b["Corallivore Density_EB_high"])


class TestInvertMetricsFullPipeline:
    """Integration tests for invertebrate metrics pipeline."""

    def test_calculate_inverts_metrics_with_biomass(
        self,
        preprocessed_invert_data,
        invert_dive_numbers,
        redirect_constants_to_test_data,
    ):
        """Test that the main inverts metrics function runs with biomass."""
        result_df = calculate_inverts_metrics(
            preprocessed_invert_data,
            invert_dive_numbers,
            "seasonal",
            include_biomass=True,
        )

        # Check that result has expected structure
        assert isinstance(result_df, pd.DataFrame)
        assert "Site" in result_df.columns
        assert "Period" in result_df.columns

        # Check all the expected columns exist
        base_metrics = [
            "Corallivore Density",
            "Detritivore Density",
            "Omnivore Density",
            "Carnivore Density",
            "Herbivore Density",
            "Total Density",
            "Total Biomass Density",
        ]
        stat_suffixes = [
            "_N",
            "_SD",
            "_SE",
            "_CI_low",
            "_CI_high",
            "_EB_low",
            "_EB_high",
        ]
        expected_columns = ["Period", "Site"]
        for metric in base_metrics:
            expected_columns.append(metric)
            expected_columns.extend([f"{metric}{suffix}" for suffix in stat_suffixes])
        for col in expected_columns:
            assert col in result_df.columns, f"Missing column: {col}"
        # Check no other columns exist
        assert len(result_df.columns) == len(
            expected_columns
        ), "Unexpected columns in result"

    def test_calculate_inverts_metrics_without_biomass(
        self,
        preprocessed_invert_data,
        invert_dive_numbers,
        redirect_constants_to_test_data,
    ):
        """Test that the main inverts metrics function runs without biomass."""
        result_df = calculate_inverts_metrics(
            preprocessed_invert_data,
            invert_dive_numbers,
            "seasonal",
            include_biomass=False,
        )

        # Check that result has expected structure
        assert isinstance(result_df, pd.DataFrame)

        # Biomass density should not be in columns when include_biomass=False
        biomass_cols = [col for col in result_df.columns if "Biomass" in col]
        assert (
            len(biomass_cols) == 0
        ), "Biomass columns should not exist when include_biomass=False"

    def test_multiple_sites_handled_correctly(self, preprocessed_invert_data):
        """Test that metrics are calculated separately for each site."""
        sites = preprocessed_invert_data["Site"].unique()
        assert len(sites) == 2
        assert "Test Site A" in sites
        assert "Test Site B" in sites

    def test_final_output_values(
        self,
        preprocessed_invert_data,
        invert_dive_numbers,
        redirect_constants_to_test_data,
    ):
        """Integration test: verify all final output values match expected calculations."""
        result_df = calculate_inverts_metrics(
            preprocessed_invert_data,
            invert_dive_numbers,
            "seasonal",
            include_biomass=False,
        )

        # Test Site A: 2 surveys
        site_a = result_df[result_df["Site"] == "Test Site A"].iloc[0]

        # Total Density: survey_001=66, survey_002=53, mean=59.5
        # N=2, SD=9.19 (standard deviation), SE=6.5 (standard error)
        # t_crit=12.706 (df=1, 95% CI), CI=confidence interval, EB=error bars (mean±SE)
        assert abs(site_a["Total Density"] - 59.5) < 0.1
        assert site_a["Total Density_N"] == 2
        assert abs(site_a["Total Density_SD"] - 9.19) < 0.1
        assert abs(site_a["Total Density_SE"] - 6.5) < 0.1
        assert abs(site_a["Total Density_CI_low"] - 0.0) < 0.1
        assert abs(site_a["Total Density_CI_high"] - 142.09) < 0.1
        assert abs(site_a["Total Density_EB_low"] - 53.0) < 0.1
        assert abs(site_a["Total Density_EB_high"] - 66.0) < 0.1

        # Herbivore Density: survey_001=50, survey_002=45, mean=47.5
        # N=2, SD=3.54, SE=2.5
        assert abs(site_a["Herbivore Density"] - 47.5) < 0.1
        assert site_a["Herbivore Density_N"] == 2
        assert abs(site_a["Herbivore Density_SD"] - 3.54) < 0.1
        assert abs(site_a["Herbivore Density_SE"] - 2.5) < 0.1
        assert abs(site_a["Herbivore Density_CI_low"] - 15.74) < 0.1
        assert abs(site_a["Herbivore Density_CI_high"] - 79.26) < 0.1
        assert abs(site_a["Herbivore Density_EB_low"] - 45.0) < 0.1
        assert abs(site_a["Herbivore Density_EB_high"] - 50.0) < 0.1

        # Carnivore Density: survey_001=5, survey_002=2, mean=3.5
        # N=2, SD=2.12, SE=1.5
        assert abs(site_a["Carnivore Density"] - 3.5) < 0.1
        assert site_a["Carnivore Density_N"] == 2
        assert abs(site_a["Carnivore Density_SD"] - 2.12) < 0.1
        assert abs(site_a["Carnivore Density_SE"] - 1.5) < 0.1
        assert abs(site_a["Carnivore Density_CI_low"] - 0.0) < 0.1
        assert abs(site_a["Carnivore Density_CI_high"] - 22.56) < 0.1
        assert abs(site_a["Carnivore Density_EB_low"] - 2.0) < 0.1
        assert abs(site_a["Carnivore Density_EB_high"] - 5.0) < 0.1

        # Omnivore Density: survey_001=8, survey_002=0, mean=4.0
        # N=2, SD=5.66, SE=4.0
        assert abs(site_a["Omnivore Density"] - 4.0) < 0.1
        assert site_a["Omnivore Density_N"] == 2
        assert abs(site_a["Omnivore Density_SD"] - 5.66) < 0.1
        assert abs(site_a["Omnivore Density_SE"] - 4.0) < 0.1
        assert abs(site_a["Omnivore Density_CI_low"] - 0.0) < 0.1
        assert abs(site_a["Omnivore Density_CI_high"] - 54.82) < 0.1
        assert abs(site_a["Omnivore Density_EB_low"] - 0.0) < 0.1
        assert abs(site_a["Omnivore Density_EB_high"] - 8.0) < 0.1

        # Detritivore Density: survey_001=3, survey_002=0, mean=1.5
        # N=2, SD=2.12, SE=1.5
        assert abs(site_a["Detritivore Density"] - 1.5) < 0.1
        assert site_a["Detritivore Density_N"] == 2
        assert abs(site_a["Detritivore Density_SD"] - 2.12) < 0.1
        assert abs(site_a["Detritivore Density_SE"] - 1.5) < 0.1
        assert abs(site_a["Detritivore Density_CI_low"] - 0.0) < 0.1
        assert abs(site_a["Detritivore Density_CI_high"] - 20.56) < 0.1
        assert abs(site_a["Detritivore Density_EB_low"] - 0.0) < 0.1
        assert abs(site_a["Detritivore Density_EB_high"] - 3.0) < 0.1

        # Corallivore Density: survey_001=0, survey_002=6, mean=3.0
        # N=2, SD=4.24, SE=3.0
        assert abs(site_a["Corallivore Density"] - 3.0) < 0.1
        assert site_a["Corallivore Density_N"] == 2
        assert abs(site_a["Corallivore Density_SD"] - 4.24) < 0.1
        assert abs(site_a["Corallivore Density_SE"] - 3.0) < 0.1
        assert abs(site_a["Corallivore Density_CI_low"] - 0.0) < 0.1
        assert abs(site_a["Corallivore Density_CI_high"] - 41.12) < 0.1
        assert abs(site_a["Corallivore Density_EB_low"] - 0.0) < 0.1
        assert abs(site_a["Corallivore Density_EB_high"] - 6.0) < 0.1

        # Test Site B: 1 survey (all SD/SE/CI/EB should be NaN)
        site_b = result_df[result_df["Site"] == "Test Site B"].iloc[0]

        # Total Density: survey_003=45
        assert abs(site_b["Total Density"] - 45.0) < 0.1
        assert site_b["Total Density_N"] == 1
        assert np.isnan(site_b["Total Density_SD"])
        assert np.isnan(site_b["Total Density_SE"])
        assert np.isnan(site_b["Total Density_CI_low"])
        assert np.isnan(site_b["Total Density_CI_high"])
        assert np.isnan(site_b["Total Density_EB_low"])
        assert np.isnan(site_b["Total Density_EB_high"])

        # Herbivore Density: survey_003=30
        assert abs(site_b["Herbivore Density"] - 30.0) < 0.1
        assert site_b["Herbivore Density_N"] == 1
        assert np.isnan(site_b["Herbivore Density_SD"])
        assert np.isnan(site_b["Herbivore Density_SE"])
        assert np.isnan(site_b["Herbivore Density_CI_low"])
        assert np.isnan(site_b["Herbivore Density_CI_high"])
        assert np.isnan(site_b["Herbivore Density_EB_low"])
        assert np.isnan(site_b["Herbivore Density_EB_high"])

        # Carnivore Density: survey_003=0 (should be 0, not NaN for the mean)
        assert abs(site_b["Carnivore Density"] - 0.0) < 0.1
        assert site_b["Carnivore Density_N"] == 1
        assert np.isnan(site_b["Carnivore Density_SD"])
        assert np.isnan(site_b["Carnivore Density_SE"])
        assert np.isnan(site_b["Carnivore Density_CI_low"])
        assert np.isnan(site_b["Carnivore Density_CI_high"])
        assert np.isnan(site_b["Carnivore Density_EB_low"])
        assert np.isnan(site_b["Carnivore Density_EB_high"])

        # Omnivore Density: survey_003=10
        assert abs(site_b["Omnivore Density"] - 10.0) < 0.1
        assert site_b["Omnivore Density_N"] == 1
        assert np.isnan(site_b["Omnivore Density_SD"])
        assert np.isnan(site_b["Omnivore Density_SE"])
        assert np.isnan(site_b["Omnivore Density_CI_low"])
        assert np.isnan(site_b["Omnivore Density_CI_high"])
        assert np.isnan(site_b["Omnivore Density_EB_low"])
        assert np.isnan(site_b["Omnivore Density_EB_high"])

        # Detritivore Density: survey_003=5
        assert abs(site_b["Detritivore Density"] - 5.0) < 0.1
        assert site_b["Detritivore Density_N"] == 1
        assert np.isnan(site_b["Detritivore Density_SD"])
        assert np.isnan(site_b["Detritivore Density_SE"])
        assert np.isnan(site_b["Detritivore Density_CI_low"])
        assert np.isnan(site_b["Detritivore Density_CI_high"])
        assert np.isnan(site_b["Detritivore Density_EB_low"])
        assert np.isnan(site_b["Detritivore Density_EB_high"])

        # Corallivore Density: survey_003=0
        assert abs(site_b["Corallivore Density"] - 0.0) < 0.1
        assert site_b["Corallivore Density_N"] == 1
        assert np.isnan(site_b["Corallivore Density_SD"])
        assert np.isnan(site_b["Corallivore Density_SE"])
        assert np.isnan(site_b["Corallivore Density_CI_low"])
        assert np.isnan(site_b["Corallivore Density_CI_high"])
        assert np.isnan(site_b["Corallivore Density_EB_low"])
        assert np.isnan(site_b["Corallivore Density_EB_high"])


class TestSubsMetricsFullPipeline:
    """Integration tests for substrate metrics pipeline."""

    def test_calculate_subs_metrics_runs(
        self, preprocessed_subs_data, subs_dive_numbers
    ):
        """Test that the main subs metrics function runs without errors."""
        result_df = calculate_subs_metrics(
            preprocessed_subs_data, subs_dive_numbers, "seasonal"
        )

        # Check that result has expected structure
        assert isinstance(result_df, pd.DataFrame)
        assert "Site" in result_df.columns
        assert "Period" in result_df.columns

        # Generate expected columns programmatically
        base_metrics = [
            "Hard Coral Cover",
            "Soft Coral Cover",
            "Fresh Algae Cover",
            "Rubble Cover",
            "Bleaching",
        ]
        stat_suffixes = [
            "_N",
            "_SD",
            "_SE",
            "_CI_low",
            "_CI_high",
            "_EB_low",
            "_EB_high",
        ]

        expected_columns = ["Period", "Site"]
        for metric in base_metrics:
            expected_columns.append(metric)
            expected_columns.extend([f"{metric}{suffix}" for suffix in stat_suffixes])

        for col in expected_columns:
            assert col in result_df.columns, f"Missing column: {col}"

        # Check no other columns exist
        assert len(result_df.columns) == len(
            expected_columns
        ), f"Unexpected columns in result. Expected {len(expected_columns)}, got {len(result_df.columns)}"

    def test_multiple_sites_handled_correctly(self, preprocessed_subs_data):
        """Test that metrics are calculated separately for each site."""
        sites = preprocessed_subs_data["Site"].unique()
        assert len(sites) == 2
        assert "Test Site A" in sites
        assert "Test Site B" in sites

    def test_coverage_values_are_percentages(
        self, preprocessed_subs_data, subs_dive_numbers
    ):
        """Test that coverage values are percentages (0-100)."""
        result_df = calculate_subs_metrics(
            preprocessed_subs_data, subs_dive_numbers, "seasonal"
        )

        # All coverage percentages should be between 0 and 100
        # Check the base metric columns (without suffixes like _N, _SD, etc.)
        coverage_cols = [
            col
            for col in result_df.columns
            if ("Cover" in col or "Bleaching" in col)
            and not any(suffix in col for suffix in ["_N", "_SD", "_SE", "_CI", "_EB"])
        ]
        for col in coverage_cols:
            assert (result_df[col] >= 0).all(), f"{col} has negative values"
            # In theory coverage can exceed 100% with overlapping coverage, but let's check for reasonable values
            # For our test data, values should be under 100%
            assert (result_df[col] <= 100).all(), f"{col} has values over 100%"

    def test_no_nan_in_final_results(self, preprocessed_subs_data, subs_dive_numbers):
        """Test that final metrics don't contain unexpected NaN values."""
        result_df = calculate_subs_metrics(
            preprocessed_subs_data, subs_dive_numbers, "seasonal"
        )

        # Coverage columns should not have NaN (they're filled with 0)
        # Check the base metric columns (without suffixes)
        coverage_cols = [
            col
            for col in result_df.columns
            if "Cover" in col
            and not any(suffix in col for suffix in ["_N", "_SD", "_SE", "_CI", "_EB"])
        ]
        for col in coverage_cols:
            assert not result_df[col].isna().any(), f"Column {col} contains NaN values"

    def test_final_output_values(self, preprocessed_subs_data, subs_dive_numbers):
        """Integration test: verify all final output values match expected calculations."""
        result_df = calculate_subs_metrics(
            preprocessed_subs_data, subs_dive_numbers, "seasonal"
        )

        # Test Site A: 2 surveys
        site_a = result_df[result_df["Site"] == "Test Site A"].iloc[0]

        # Hard Coral Cover: survey_001=62.5%, survey_002=37.5%
        # N=2, SD=17.68 (standard deviation), SE=12.5 (standard error)
        # t_crit=12.706 (df=1, 95% CI), CI=confidence interval, EB=error bars (mean±SE)
        assert abs(site_a["Hard Coral Cover"] - 50.0) < 0.1
        assert site_a["Hard Coral Cover_N"] == 2
        assert abs(site_a["Hard Coral Cover_SD"] - 17.68) < 0.1
        assert abs(site_a["Hard Coral Cover_SE"] - 12.5) < 0.1
        assert abs(site_a["Hard Coral Cover_CI_low"] - 0.0) < 0.1
        assert abs(site_a["Hard Coral Cover_CI_high"] - 208.83) < 0.1
        assert abs(site_a["Hard Coral Cover_EB_low"] - 37.5) < 0.1
        assert abs(site_a["Hard Coral Cover_EB_high"] - 62.5) < 0.1

        # Soft Coral Cover: survey_001=16.67%, survey_002=25.0%
        # N=2, SD=5.89, SE=4.17
        assert abs(site_a["Soft Coral Cover"] - 20.835) < 0.1
        assert site_a["Soft Coral Cover_N"] == 2
        assert abs(site_a["Soft Coral Cover_SD"] - 5.89) < 0.1
        assert abs(site_a["Soft Coral Cover_SE"] - 4.17) < 0.1
        assert abs(site_a["Soft Coral Cover_CI_low"] - 0.0) < 0.1
        assert abs(site_a["Soft Coral Cover_CI_high"] - 73.82) < 0.1
        assert abs(site_a["Soft Coral Cover_EB_low"] - 16.665) < 0.1
        assert abs(site_a["Soft Coral Cover_EB_high"] - 25.005) < 0.1

        # Fresh Algae Cover: survey_001=12.5%, survey_002=20.83%
        # N=2, SD=5.89, SE=4.17
        assert abs(site_a["Fresh Algae Cover"] - 16.665) < 0.1
        assert site_a["Fresh Algae Cover_N"] == 2
        assert abs(site_a["Fresh Algae Cover_SD"] - 5.89) < 0.1
        assert abs(site_a["Fresh Algae Cover_SE"] - 4.17) < 0.1
        assert abs(site_a["Fresh Algae Cover_CI_low"] - 0.0) < 0.1
        assert abs(site_a["Fresh Algae Cover_CI_high"] - 69.65) < 0.1
        assert abs(site_a["Fresh Algae Cover_EB_low"] - 12.495) < 0.1
        assert abs(site_a["Fresh Algae Cover_EB_high"] - 20.835) < 0.1

        # Rubble Cover: survey_001=8.33%, survey_002=16.67%
        # N=2, SD=5.89, SE=4.17
        assert abs(site_a["Rubble Cover"] - 12.5) < 0.1
        assert site_a["Rubble Cover_N"] == 2
        assert abs(site_a["Rubble Cover_SD"] - 5.89) < 0.1
        assert abs(site_a["Rubble Cover_SE"] - 4.17) < 0.1
        assert abs(site_a["Rubble Cover_CI_low"] - 0.0) < 0.1
        assert abs(site_a["Rubble Cover_CI_high"] - 65.48) < 0.1
        assert abs(site_a["Rubble Cover_EB_low"] - 8.33) < 0.1
        assert abs(site_a["Rubble Cover_EB_high"] - 16.67) < 0.1

        # Bleaching: survey_001=8.33%, survey_002=37.5%
        # N=2, SD=20.61, SE=14.58
        assert abs(site_a["Bleaching"] - 22.915) < 0.1
        assert site_a["Bleaching_N"] == 2
        assert abs(site_a["Bleaching_SD"] - 20.61) < 0.1
        assert abs(site_a["Bleaching_SE"] - 14.58) < 0.1
        assert abs(site_a["Bleaching_CI_low"] - 0.0) < 0.1
        assert abs(site_a["Bleaching_CI_high"] - 208.13) < 0.1
        assert abs(site_a["Bleaching_EB_low"] - 8.335) < 0.1
        assert abs(site_a["Bleaching_EB_high"] - 37.495) < 0.1

        # Test Site B: 1 survey (all SD/SE/CI/EB should be NaN)
        site_b = result_df[result_df["Site"] == "Test Site B"].iloc[0]

        # Hard Coral Cover: survey_003=41.67%
        assert abs(site_b["Hard Coral Cover"] - 41.67) < 0.1
        assert site_b["Hard Coral Cover_N"] == 1
        assert np.isnan(site_b["Hard Coral Cover_SD"])
        assert np.isnan(site_b["Hard Coral Cover_SE"])
        assert np.isnan(site_b["Hard Coral Cover_CI_low"])
        assert np.isnan(site_b["Hard Coral Cover_CI_high"])
        assert np.isnan(site_b["Hard Coral Cover_EB_low"])
        assert np.isnan(site_b["Hard Coral Cover_EB_high"])

        # Soft Coral Cover: survey_003=29.17%
        assert abs(site_b["Soft Coral Cover"] - 29.17) < 0.1
        assert site_b["Soft Coral Cover_N"] == 1
        assert np.isnan(site_b["Soft Coral Cover_SD"])
        assert np.isnan(site_b["Soft Coral Cover_SE"])
        assert np.isnan(site_b["Soft Coral Cover_CI_low"])
        assert np.isnan(site_b["Soft Coral Cover_CI_high"])
        assert np.isnan(site_b["Soft Coral Cover_EB_low"])
        assert np.isnan(site_b["Soft Coral Cover_EB_high"])

        # Fresh Algae Cover: survey_003=16.67%
        assert abs(site_b["Fresh Algae Cover"] - 16.67) < 0.1
        assert site_b["Fresh Algae Cover_N"] == 1
        assert np.isnan(site_b["Fresh Algae Cover_SD"])
        assert np.isnan(site_b["Fresh Algae Cover_SE"])
        assert np.isnan(site_b["Fresh Algae Cover_CI_low"])
        assert np.isnan(site_b["Fresh Algae Cover_CI_high"])
        assert np.isnan(site_b["Fresh Algae Cover_EB_low"])
        assert np.isnan(site_b["Fresh Algae Cover_EB_high"])

        # Rubble Cover: survey_003=12.5%
        assert abs(site_b["Rubble Cover"] - 12.5) < 0.1
        assert site_b["Rubble Cover_N"] == 1
        assert np.isnan(site_b["Rubble Cover_SD"])
        assert np.isnan(site_b["Rubble Cover_SE"])
        assert np.isnan(site_b["Rubble Cover_CI_low"])
        assert np.isnan(site_b["Rubble Cover_CI_high"])
        assert np.isnan(site_b["Rubble Cover_EB_low"])
        assert np.isnan(site_b["Rubble Cover_EB_high"])

        # Bleaching: survey_003=0%
        assert abs(site_b["Bleaching"] - 0.0) < 0.1
        assert site_b["Bleaching_N"] == 1
        assert np.isnan(site_b["Bleaching_SD"])
        assert np.isnan(site_b["Bleaching_SE"])
        assert np.isnan(site_b["Bleaching_CI_low"])
        assert np.isnan(site_b["Bleaching_CI_high"])
        assert np.isnan(site_b["Bleaching_EB_low"])
        assert np.isnan(site_b["Bleaching_EB_high"])
