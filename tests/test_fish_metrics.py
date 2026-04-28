"""
Tests for fish metrics calculations.
"""

import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from fish_metrics import (
    calculate_fish_metrics,
    calculate_commercial_count_and_density,
    calculate_commercial_biomass,
)
from fish_and_inverts_shared_metrics import (
    calculate_biomass,
    calculate_total_count_and_density,
    calculate_total_biomass_and_density,
    calculate_herbivore_density,
    calculate_carnivore_density,
    calculate_omnivore_density,
    calculate_detritivore_density,
    calculate_corallivore_density,
)
from utils import create_daily_df, add_periods


class TestFishBiomassCalculation:
    """Test biomass calculations for fish."""

    def test_biomass_calculation_values(
        self, preprocessed_fish_data, test_constants_dir
    ):
        """Test that biomass is calculated correctly using the formula."""
        daily_df = create_daily_df(preprocessed_fish_data, "fish")
        biomass_df = calculate_biomass(
            daily_df, str(test_constants_dir / "biomass_coeffs_fish.csv")
        )

        # Check that biomass column was added
        assert "Total Biomass" in biomass_df.columns

        # Check that no biomass values are NaN
        assert not biomass_df["Total Biomass"].isna().any()

        # Check that all biomass values are positive
        assert (biomass_df["Total Biomass"] >= 0).all()

        # Test specific calculation for known values
        # For Parrotfish - Other: size 10-20 (use midpoint 15), count 5
        # Coeff_a = 0.0206, Coeff_b = 2.949
        # Biomass = 5 * 0.0206 * (15 ^ 2.949) ≈ 5 * 0.0206 * 2617.99 ≈ 269.65
        parrotfish_row = biomass_df[
            (biomass_df["Species"] == "Parrotfish - Other")
            & (biomass_df["Size"] == 15)
            & (biomass_df["Survey_ID"] == "test_survey_001")
        ]
        expected_biomass = 5 * 0.0206 * (15**2.949)
        assert len(parrotfish_row) == 1
        assert abs(parrotfish_row.iloc[0]["Total Biomass"] - expected_biomass) < 0.01


class TestFishDensityCalculation:
    """Test density calculations for fish."""

    def test_total_count_and_density(self, preprocessed_fish_data, fish_dive_numbers):
        """Test total count and density calculations."""
        daily_df = create_daily_df(preprocessed_fish_data, "fish")
        daily_df = add_periods(daily_df, "seasonal")

        result_df = calculate_total_count_and_density(daily_df, fish_dive_numbers)

        # Check that the result has the expected columns
        assert "Total Density" in result_df.columns
        assert "Survey_ID" in result_df.columns
        assert "Site" in result_df.columns

        # For test_survey_001, total count = 5+10+3+20+2 = 40, dives = 1, density = 40
        survey_001_result = result_df[result_df["Survey_ID"] == "test_survey_001"]
        assert len(survey_001_result) == 1
        assert abs(survey_001_result.iloc[0]["Total Density"] - 40.0) < 0.01


class TestCommercialFishMetrics:
    """Test commercial fish metrics."""

    def test_commercial_fish_identification(
        self, preprocessed_fish_data, test_constants_dir
    ):
        """Test that commercial fish are correctly identified."""
        # Read commercial fish list
        commercial_fish = (
            pd.read_csv(test_constants_dir / "commercial_fish.csv", header=None)
            .iloc[:, 0]
            .tolist()
        )

        # Check that expected species are in the list
        assert "Parrotfish - Other" in commercial_fish
        assert "Surgeonfish - Other" in commercial_fish
        assert "Fusilier" in commercial_fish

        # Check that non-commercial fish are not in the list
        assert "Damselfish" not in commercial_fish
        assert "Grouper" not in commercial_fish

    def test_commercial_density_calculation(
        self, preprocessed_fish_data, fish_dive_numbers, redirect_constants_to_test_data
    ):
        """Test that commercial fish density is calculated correctly per survey."""
        daily_df = create_daily_df(preprocessed_fish_data, "fish")
        daily_df = add_periods(daily_df, "seasonal")
        result_df = calculate_commercial_count_and_density(daily_df, fish_dive_numbers)

        # Verify structure
        assert "Commercial Density" in result_df.columns
        assert "Survey_ID" in result_df.columns

        # Test specific values
        # test_survey_001: Parrotfish (5) + Surgeonfish (10) = 15 over 1 dive -> density = 15
        survey_001 = result_df[result_df["Survey_ID"] == "test_survey_001"]
        assert len(survey_001) == 1
        assert abs(survey_001.iloc[0]["Commercial Density"] - 15.0) < 0.01

        # test_survey_002: Parrotfish (4) + Surgeonfish (8) + Fusilier (15) = 27 over 1 dive -> density = 27
        survey_002 = result_df[result_df["Survey_ID"] == "test_survey_002"]
        assert len(survey_002) == 1
        assert abs(survey_002.iloc[0]["Commercial Density"] - 27.0) < 0.01

        # test_survey_003: Parrotfish (6) over 1 dive -> density = 6
        survey_003 = result_df[result_df["Survey_ID"] == "test_survey_003"]
        assert len(survey_003) == 1
        assert abs(survey_003.iloc[0]["Commercial Density"] - 6.0) < 0.01

    def test_commercial_biomass_calculation(
        self,
        preprocessed_fish_data,
        fish_dive_numbers,
        test_constants_dir,
        redirect_constants_to_test_data,
    ):
        """Test that commercial biomass is calculated correctly per survey."""
        daily_df = create_daily_df(preprocessed_fish_data, "fish")
        daily_df = add_periods(daily_df, "seasonal")
        daily_df = calculate_biomass(
            daily_df, str(test_constants_dir / "biomass_coeffs_fish.csv")
        )
        result_df = calculate_commercial_biomass(daily_df, fish_dive_numbers)

        # Verify structure
        assert "Commercial Biomass Density" in result_df.columns
        assert "Survey_ID" in result_df.columns

        # Test specific values
        # test_survey_001:
        # - Parrotfish: 5 * 0.0206 * (15^2.949) ≈ 269.65 grams
        # - Surgeonfish: 10 * 0.0157 * (7.5^3.061) ≈ 46.62 grams
        # - Total: 316.27 grams = 0.31627 kg
        # - Density: 0.31627 kg / 1 dive
        survey_001 = result_df[result_df["Survey_ID"] == "test_survey_001"]
        assert len(survey_001) == 1
        expected_biomass_001 = (
            5 * 0.0206 * (15**2.949) + 10 * 0.0157 * (7.5**3.061)
        ) / 1000  # Convert to kg
        assert (
            abs(survey_001.iloc[0]["Commercial Biomass Density"] - expected_biomass_001)
            < 0.01
        )

        # test_survey_002:
        # - Parrotfish: 4 * 0.0206 * (15^2.949) ≈ 215.72 grams
        # - Surgeonfish: 8 * 0.0157 * (7.5^3.061) ≈ 37.30 grams
        # - Fusilier: 15 * 0.0061 * (15^3.118) ≈ 279.14 grams
        # - Total: 532.16 grams = 0.53216 kg
        # - Density: 0.53216 kg / 1 dive
        survey_002 = result_df[result_df["Survey_ID"] == "test_survey_002"]
        assert len(survey_002) == 1
        expected_biomass_002 = (
            4 * 0.0206 * (15**2.949)
            + 8 * 0.0157 * (7.5**3.061)
            + 15 * 0.0061 * (15**3.118)
        ) / 1000  # Convert to kg
        assert (
            abs(survey_002.iloc[0]["Commercial Biomass Density"] - expected_biomass_002)
            < 0.01
        )

        # test_survey_003:
        # - Parrotfish: 6 * 0.0206 * (7.5^2.949) ≈ 40.43 grams
        # - Total: 40.43 grams = 0.04043 kg
        # - Density: 0.04043 kg / 1 dive
        survey_003 = result_df[result_df["Survey_ID"] == "test_survey_003"]
        assert len(survey_003) == 1
        expected_biomass_003 = (6 * 0.0206 * (7.5**2.949)) / 1000  # Convert to kg
        assert (
            abs(survey_003.iloc[0]["Commercial Biomass Density"] - expected_biomass_003)
            < 0.01
        )


class TestFishFoodGroups:
    """Test fish food group density calculations."""

    def test_herbivore_fish_identification(self, test_constants_dir):
        """Test that herbivore fish are correctly identified."""
        herbivore_fish = (
            pd.read_csv(test_constants_dir / "herbivore_fish.csv", header=None)
            .iloc[:, 0]
            .tolist()
        )

        assert "Surgeonfish - Other" in herbivore_fish
        assert "Fusilier" in herbivore_fish

    def test_carnivore_fish_identification(self, test_constants_dir):
        """Test that carnivore fish are correctly identified."""
        carnivore_fish = (
            pd.read_csv(test_constants_dir / "carnivore_fish.csv", header=None)
            .iloc[:, 0]
            .tolist()
        )

        assert "Grouper" in carnivore_fish

    def test_detritivore_fish_identification(self, test_constants_dir):
        """Test that detritivore fish are correctly identified."""
        detritivore_fish = (
            pd.read_csv(test_constants_dir / "detritivore_fish.csv", header=None)
            .iloc[:, 0]
            .tolist()
        )

        assert "Rabbitfish" in detritivore_fish

    def test_omnivore_fish_identification(self, test_constants_dir):
        """Test that omnivore fish are correctly identified."""
        omnivore_fish = (
            pd.read_csv(test_constants_dir / "omnivore_fish.csv", header=None)
            .iloc[:, 0]
            .tolist()
        )

        assert "Parrotfish - Other" in omnivore_fish

    def test_corallivore_fish_identification(self, test_constants_dir):
        """Test that corallivore fish are correctly identified."""
        corallivore_fish = (
            pd.read_csv(test_constants_dir / "corallivore_fish.csv", header=None)
            .iloc[:, 0]
            .tolist()
        )

        assert "Damselfish" in corallivore_fish

    def test_fish_herbivore_density_calculation(
        self, preprocessed_fish_data, fish_dive_numbers, redirect_constants_to_test_data
    ):
        """Test that herbivore density is calculated correctly per survey."""
        daily_df = create_daily_df(preprocessed_fish_data, "fish")
        daily_df = add_periods(daily_df, "seasonal")
        result_df = calculate_herbivore_density(daily_df, fish_dive_numbers, "fish")

        # Verify structure
        assert "Herbivore Density" in result_df.columns
        assert "Survey_ID" in result_df.columns

        # Test specific values
        # test_survey_001: Surgeonfish - Other (10) over 1 dive -> density = 10
        survey_001 = result_df[result_df["Survey_ID"] == "test_survey_001"]
        assert len(survey_001) == 1
        assert abs(survey_001.iloc[0]["Herbivore Density"] - 10.0) < 0.01

        # test_survey_002: Surgeonfish - Other (8) + Fusilier (15) = 23 over 1 dive -> density = 23
        survey_002 = result_df[result_df["Survey_ID"] == "test_survey_002"]
        assert len(survey_002) == 1
        assert abs(survey_002.iloc[0]["Herbivore Density"] - 23.0) < 0.01

        # test_survey_003: No herbivores -> not in results (treated as 0)
        survey_003 = result_df[result_df["Survey_ID"] == "test_survey_003"]
        assert len(survey_003) == 0  # No row when density is 0

    def test_fish_carnivore_density_calculation(
        self, preprocessed_fish_data, fish_dive_numbers, redirect_constants_to_test_data
    ):
        """Test that carnivore density is calculated correctly per survey."""
        daily_df = create_daily_df(preprocessed_fish_data, "fish")
        daily_df = add_periods(daily_df, "seasonal")
        result_df = calculate_carnivore_density(daily_df, fish_dive_numbers, "fish")

        # Verify structure
        assert "Carnivore Density" in result_df.columns
        assert "Survey_ID" in result_df.columns

        # Test specific values
        # test_survey_001: Grouper (2) over 1 dive -> density = 2
        survey_001 = result_df[result_df["Survey_ID"] == "test_survey_001"]
        assert len(survey_001) == 1
        assert abs(survey_001.iloc[0]["Carnivore Density"] - 2.0) < 0.01

        # test_survey_002: No carnivores -> not in results (treated as 0)
        survey_002 = result_df[result_df["Survey_ID"] == "test_survey_002"]
        assert len(survey_002) == 0  # No row when density is 0

        # test_survey_003: Grouper (3) over 1 dive -> density = 3
        survey_003 = result_df[result_df["Survey_ID"] == "test_survey_003"]
        assert len(survey_003) == 1
        assert abs(survey_003.iloc[0]["Carnivore Density"] - 3.0) < 0.01

    def test_fish_omnivore_density_calculation(
        self, preprocessed_fish_data, fish_dive_numbers, redirect_constants_to_test_data
    ):
        """Test that omnivore density is calculated correctly per survey."""
        daily_df = create_daily_df(preprocessed_fish_data, "fish")
        daily_df = add_periods(daily_df, "seasonal")
        result_df = calculate_omnivore_density(daily_df, fish_dive_numbers, "fish")

        # Verify structure
        assert "Omnivore Density" in result_df.columns
        assert "Survey_ID" in result_df.columns

        # Test specific values
        # test_survey_001: Parrotfish - Other (5) over 1 dive -> density = 5
        survey_001 = result_df[result_df["Survey_ID"] == "test_survey_001"]
        assert len(survey_001) == 1
        assert abs(survey_001.iloc[0]["Omnivore Density"] - 5.0) < 0.01

        # test_survey_002: Parrotfish - Other (4) over 1 dive -> density = 4
        survey_002 = result_df[result_df["Survey_ID"] == "test_survey_002"]
        assert len(survey_002) == 1
        assert abs(survey_002.iloc[0]["Omnivore Density"] - 4.0) < 0.01

        # test_survey_003: Parrotfish - Other (6) over 1 dive -> density = 6
        survey_003 = result_df[result_df["Survey_ID"] == "test_survey_003"]
        assert len(survey_003) == 1
        assert abs(survey_003.iloc[0]["Omnivore Density"] - 6.0) < 0.01

    def test_fish_detritivore_density_calculation(
        self, preprocessed_fish_data, fish_dive_numbers, redirect_constants_to_test_data
    ):
        """Test that detritivore density is calculated correctly per survey."""
        daily_df = create_daily_df(preprocessed_fish_data, "fish")
        daily_df = add_periods(daily_df, "seasonal")
        result_df = calculate_detritivore_density(daily_df, fish_dive_numbers, "fish")

        # Verify structure
        assert "Detritivore Density" in result_df.columns
        assert "Survey_ID" in result_df.columns

        # Test specific values
        # test_survey_001: Rabbitfish (3) over 1 dive -> density = 3
        survey_001 = result_df[result_df["Survey_ID"] == "test_survey_001"]
        assert len(survey_001) == 1
        assert abs(survey_001.iloc[0]["Detritivore Density"] - 3.0) < 0.01

        # test_survey_002: No detritivores -> not in results (treated as 0)
        survey_002 = result_df[result_df["Survey_ID"] == "test_survey_002"]
        assert len(survey_002) == 0  # No row when density is 0

        # test_survey_003: No detritivores -> not in results (treated as 0)
        survey_003 = result_df[result_df["Survey_ID"] == "test_survey_003"]
        assert len(survey_003) == 0  # No row when density is 0

    def test_fish_corallivore_density_calculation(
        self, preprocessed_fish_data, fish_dive_numbers, redirect_constants_to_test_data
    ):
        """Test that corallivore density is calculated correctly per survey."""
        daily_df = create_daily_df(preprocessed_fish_data, "fish")
        daily_df = add_periods(daily_df, "seasonal")
        result_df = calculate_corallivore_density(daily_df, fish_dive_numbers, "fish")

        # Verify structure
        assert "Corallivore Density" in result_df.columns
        assert "Survey_ID" in result_df.columns

        # Test specific values
        # test_survey_001: Damselfish (20) over 1 dive -> density = 20
        survey_001 = result_df[result_df["Survey_ID"] == "test_survey_001"]
        assert len(survey_001) == 1
        assert abs(survey_001.iloc[0]["Corallivore Density"] - 20.0) < 0.01

        # test_survey_002: No corallivores -> not in results (treated as 0)
        survey_002 = result_df[result_df["Survey_ID"] == "test_survey_002"]
        assert len(survey_002) == 0  # No row when density is 0

        # test_survey_003: Damselfish (25) over 1 dive -> density = 25
        survey_003 = result_df[result_df["Survey_ID"] == "test_survey_003"]
        assert len(survey_003) == 1
        assert abs(survey_003.iloc[0]["Corallivore Density"] - 25.0) < 0.01

    def test_species_not_in_any_trophic_group(
        self, preprocessed_fish_data, fish_dive_numbers, redirect_constants_to_test_data
    ):
        """Test that species not found in any trophic group CSV raise an error."""
        # Create a modified dataset with a species that doesn't exist in any CSV
        modified_data = preprocessed_fish_data.copy()
        # Add a fake species row
        new_row = modified_data.iloc[0].copy()
        new_row["Species"] = "Unknown Fish Species"
        new_row["Total"] = 100
        modified_data = pd.concat(
            [modified_data, pd.DataFrame([new_row])], ignore_index=True
        )

        # Should raise ValueError when trying to calculate metrics with unknown species
        with pytest.raises(ValueError, match="not found in any trophic group CSV"):
            calculate_fish_metrics(modified_data, fish_dive_numbers, "seasonal")
