"""
Tests for substrate metrics calculations.
"""

import sys
from pathlib import Path

import pandas as pd
import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from subs_metrics import (
    calculate_subs_metrics,
    calculate_hard_coral_cover,
    calculate_soft_coral_cover,
    calculate_fresh_algae_cover,
    calculate_rubble_cover,
    calculate_bleaching,
)
from utils import create_survey_df


class TestHardCoralCover:
    """Test hard coral cover calculations."""

    def test_hard_coral_cover_calculation(self, preprocessed_subs_data):
        """Test that hard coral cover is calculated correctly."""
        survey_df = create_survey_df(preprocessed_subs_data, "subs", "seasonal")

        result_df = calculate_hard_coral_cover(survey_df)

        # Check columns
        assert "Hard Coral Cover" in result_df.columns
        assert "Survey_ID" in result_df.columns
        assert "Site" in result_df.columns

        # For test_survey_001:
        # Hard Coral Massive (Healthy): 40, Hard Coral Foliose (Healthy): 25, Hard Coral Massive (Fully Bleaching): 10
        # Total = 75, Dives = 1
        # Coverage = (75 / 1) / 120 * 100 = 62.5%
        survey_001_result = result_df[result_df["Survey_ID"] == "test_survey_001"]
        assert len(survey_001_result) == 1
        expected_cover = (75 / 1) / 120 * 100
        assert (
            abs(survey_001_result.iloc[0]["Hard Coral Cover"] - expected_cover) < 0.01
        )

    def test_hard_coral_identification(self, preprocessed_subs_data):
        """Test that hard coral groups are correctly identified regardless of health status."""
        survey_df = create_survey_df(preprocessed_subs_data, "subs", "seasonal")

        # Test that hard coral groups are identified
        hard_coral_groups = survey_df[
            survey_df["Group"].str.contains("Hard Coral", na=False)
        ]
        unique_groups = hard_coral_groups["Group"].unique()

        assert "Hard Coral Massive" in unique_groups
        assert "Hard Coral Foliose" in unique_groups

        # Test that hard coral with different health statuses are counted
        # Check that we have both healthy and bleached hard coral
        hard_coral_statuses = hard_coral_groups["Status"].unique()
        assert "Healthy" in hard_coral_statuses
        assert "Fully Bleaching" in hard_coral_statuses
        assert "Partially Bleaching" in hard_coral_statuses

        # Verify that bleached hard coral is still counted as hard coral
        bleached_hard_coral = survey_df[
            (survey_df["Group"].str.contains("Hard Coral", na=False))
            & (
                survey_df["Status"].str.contains(
                    "Fully Bleaching|Partially Bleaching", na=False
                )
            )
        ]
        assert (
            len(bleached_hard_coral) > 0
        ), "Should have bleached hard coral in test data"

        # Total hard coral count should include both healthy and bleached
        total_hard_coral_count = hard_coral_groups["Total"].sum()
        healthy_count = hard_coral_groups[hard_coral_groups["Status"] == "Healthy"][
            "Total"
        ].sum()
        bleached_count = (
            hard_coral_groups[
                hard_coral_groups["Status"].str.contains("Fully Bleaching", na=False)
            ]["Total"].sum()
            + hard_coral_groups[
                hard_coral_groups["Status"].str.contains(
                    "Partially Bleaching", na=False
                )
            ]["Total"].sum()
        )
        assert total_hard_coral_count == healthy_count + bleached_count


class TestSoftCoralCover:
    """Test soft coral cover calculations."""

    def test_soft_coral_cover_calculation(self, preprocessed_subs_data):
        """Test that soft coral cover is calculated correctly."""
        survey_df = create_survey_df(preprocessed_subs_data, "subs", "seasonal")

        result_df = calculate_soft_coral_cover(survey_df)

        # Check columns
        assert "Soft Coral Cover" in result_df.columns

        # For test_survey_001:
        # Soft Coral Gorgonian: 20
        # Coverage = (20 / 1) / 120 * 100 = 16.67%
        survey_001_result = result_df[result_df["Survey_ID"] == "test_survey_001"]
        assert len(survey_001_result) == 1
        expected_cover = (20 / 1) / 120 * 100
        assert (
            abs(survey_001_result.iloc[0]["Soft Coral Cover"] - expected_cover) < 0.01
        )


class TestFreshAlgaeCover:
    """Test fresh algae cover calculations."""

    def test_fresh_algae_cover_calculation(self, preprocessed_subs_data):
        """Test that fresh algae cover is calculated correctly."""
        survey_df = create_survey_df(preprocessed_subs_data, "subs", "seasonal")

        result_df = calculate_fresh_algae_cover(survey_df)

        # Check columns
        assert "Fresh Algae Cover" in result_df.columns

        # For test_survey_001:
        # Algae Turf: 15
        # Coverage = (15 / 1) / 120 * 100 = 12.5%
        survey_001_result = result_df[result_df["Survey_ID"] == "test_survey_001"]
        assert len(survey_001_result) == 1
        expected_cover = (15 / 1) / 120 * 100
        assert (
            abs(survey_001_result.iloc[0]["Fresh Algae Cover"] - expected_cover) < 0.01
        )

        # For test_survey_002:
        # Algae Macro: 25
        # Coverage = (25 / 1) / 120 * 100 = 20.83%
        survey_002_result = result_df[result_df["Survey_ID"] == "test_survey_002"]
        assert len(survey_002_result) == 1
        expected_cover = (25 / 1) / 120 * 100
        assert (
            abs(survey_002_result.iloc[0]["Fresh Algae Cover"] - expected_cover) < 0.01
        )


class TestRubbleCover:
    """Test rubble cover calculations."""

    def test_rubble_cover_calculation(self, preprocessed_subs_data):
        """Test that rubble cover is calculated correctly."""
        survey_df = create_survey_df(preprocessed_subs_data, "subs", "seasonal")

        result_df = calculate_rubble_cover(survey_df)

        # Check columns
        assert "Rubble Cover" in result_df.columns

        # For test_survey_001:
        # Substrate Rubble: 10
        # Coverage = (10 / 1) / 120 * 100 = 8.33%
        survey_001_result = result_df[result_df["Survey_ID"] == "test_survey_001"]
        assert len(survey_001_result) == 1
        expected_cover = (10 / 1) / 120 * 100
        assert abs(survey_001_result.iloc[0]["Rubble Cover"] - expected_cover) < 0.01


class TestBleaching:
    """Test bleaching calculations."""

    def test_bleaching_calculation(self, preprocessed_subs_data):
        """Test that bleaching percentage is calculated correctly."""
        survey_df = create_survey_df(preprocessed_subs_data, "subs", "seasonal")

        result_df = calculate_bleaching(survey_df)

        # Check columns
        assert "Bleaching" in result_df.columns

        # For test_survey_001:
        # Hard Coral Massive Fully Bleaching: 10
        # Bleaching = (10 / 120) * 100 = 8.33%
        survey_001_result = result_df[result_df["Survey_ID"] == "test_survey_001"]
        if len(survey_001_result) > 0:
            expected_bleaching = (10 / 120) * 100
            assert (
                abs(survey_001_result.iloc[0]["Bleaching"] - expected_bleaching) < 0.1
            )

        # For test_survey_002:
        # Hard Coral Massive Partially Bleaching: 45
        # Bleaching = (45 / 120) * 100 = 37.5%
        survey_002_result = result_df[result_df["Survey_ID"] == "test_survey_002"]
        if len(survey_002_result) > 0:
            expected_bleaching = 37.5
            assert (
                abs(survey_002_result.iloc[0]["Bleaching"] - expected_bleaching) < 0.1
            )

    def test_no_bleaching(self, preprocessed_subs_data):
        """Test handling of surveys with no bleaching."""
        survey_df = create_survey_df(preprocessed_subs_data, "subs", "seasonal")

        result_df = calculate_bleaching(survey_df)

        # test_survey_003 has no bleached coral (all healthy)
        survey_003_result = result_df[result_df["Survey_ID"] == "test_survey_003"]
        # If there's no bleaching, the survey should have 0% bleaching
        if len(survey_003_result) > 0:
            assert survey_003_result.iloc[0]["Bleaching"] == 0
