"""
Tests for invertebrate metrics calculations.
"""

import sys
from pathlib import Path

import pandas as pd
import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from invert_metrics import calculate_inverts_metrics, calculate_species_richness
from fish_and_inverts_shared_metrics import (
    calculate_biomass,
    calculate_total_count_and_density,
    calculate_herbivore_density,
    calculate_carnivore_density,
    calculate_omnivore_density,
    calculate_detritivore_density,
    calculate_corallivore_density,
)
from utils import create_daily_df, add_periods


class TestInvertBiomassCalculation:
    """Test biomass calculations for invertebrates."""

    def test_biomass_calculation_values(
        self, preprocessed_invert_data, test_constants_dir
    ):
        """Test that biomass is calculated correctly for invertebrates."""
        daily_df = create_daily_df(preprocessed_invert_data, "inverts")
        biomass_df = calculate_biomass(
            daily_df, str(test_constants_dir / "biomass_coeffs_inverts.csv")
        )

        # Check that biomass column was added
        assert "Total Biomass" in biomass_df.columns

        # Check that no biomass values are NaN
        assert not biomass_df["Total Biomass"].isna().any()

        # Check that all biomass values are positive or zero
        assert (biomass_df["Total Biomass"] >= 0).all()

        # Test specific calculation
        # For Sea Urchins - Diadema: size 5-10 (midpoint 7.5), count 50
        # Coeff_a = 0.0050, Coeff_b = 2.500
        # Biomass = 50 * 0.0050 * (7.5 ^ 2.500)
        urchin_row = biomass_df[
            (biomass_df["Species"] == "Sea Urchins - Diadema")
            & (biomass_df["Size"] == 7.5)
            & (biomass_df["Survey_ID"] == "test_survey_001")
        ]
        expected_biomass = 50 * 0.0050 * (7.5**2.500)
        assert len(urchin_row) == 1
        assert abs(urchin_row.iloc[0]["Total Biomass"] - expected_biomass) < 0.01


class TestInvertDensityCalculation:
    """Test density calculations for invertebrates."""

    def test_total_count_and_density(
        self, preprocessed_invert_data, invert_dive_numbers
    ):
        """Test total count and density calculations."""
        daily_df = create_daily_df(preprocessed_invert_data, "inverts")
        from utils import add_periods

        daily_df = add_periods(daily_df, "seasonal")

        result_df = calculate_total_count_and_density(daily_df, invert_dive_numbers)

        # Check that the result has the expected columns
        assert "Total Density" in result_df.columns
        assert "Survey_ID" in result_df.columns
        assert "Site" in result_df.columns

        # For test_survey_001, total count = 50+5+3+8 = 66, dives = 1, density = 66
        survey_001_result = result_df[result_df["Survey_ID"] == "test_survey_001"]
        assert len(survey_001_result) == 1
        assert abs(survey_001_result.iloc[0]["Total Density"] - 66.0) < 0.01


class TestInvertFoodGroups:
    """Test invert food group density calculations."""

    def test_herbivore_inverts_identification(self, test_constants_dir):
        """Test that herbivore invertebrates are correctly identified."""
        herbivore_inverts = (
            pd.read_csv(test_constants_dir / "herbivore_inverts.csv", header=None)
            .iloc[:, 0]
            .tolist()
        )

        assert "Sea Urchins - Diadema" in herbivore_inverts

    def test_carnivore_inverts_identification(self, test_constants_dir):
        """Test that carnivore invertebrates are correctly identified."""
        carnivore_inverts = (
            pd.read_csv(test_constants_dir / "carnivore_inverts.csv", header=None)
            .iloc[:, 0]
            .tolist()
        )

        assert "Sea Stars - Crown of Thorns" in carnivore_inverts
        assert "Gastropods - Cone" in carnivore_inverts

    def test_detritivore_inverts_identification(self, test_constants_dir):
        """Test that detritivore invertebrates are correctly identified."""
        detritivore_inverts = (
            pd.read_csv(test_constants_dir / "detritivore_inverts.csv", header=None)
            .iloc[:, 0]
            .tolist()
        )

        assert "Bivalves - Giant Clam" in detritivore_inverts

    def test_omnivore_inverts_identification(self, test_constants_dir):
        """Test that omnivore invertebrates are correctly identified."""
        omnivore_inverts = (
            pd.read_csv(test_constants_dir / "omnivore_inverts.csv", header=None)
            .iloc[:, 0]
            .tolist()
        )

        assert "Sea Cucumbers - Other" in omnivore_inverts

    def test_corallivore_inverts_identification(self, test_constants_dir):
        """Test that corallivore invertebrates are correctly identified."""
        corallivore_inverts = (
            pd.read_csv(test_constants_dir / "corallivore_inverts.csv", header=None)
            .iloc[:, 0]
            .tolist()
        )

        assert "Gastropods - Tiger Cowrie" in corallivore_inverts

    def test_inverts_herbivore_density_calculation(
        self,
        preprocessed_invert_data,
        invert_dive_numbers,
        redirect_constants_to_test_data,
    ):
        """Test that herbivore density is calculated correctly per survey."""
        daily_df = create_daily_df(preprocessed_invert_data, "inverts")
        daily_df = add_periods(daily_df, "seasonal")
        result_df = calculate_herbivore_density(
            daily_df, invert_dive_numbers, "inverts"
        )

        # Verify structure
        assert "Herbivore Density" in result_df.columns
        assert "Survey_ID" in result_df.columns

        # Test specific values
        # test_survey_001: Sea Urchins - Diadema (50) over 1 dive -> density = 50
        survey_001 = result_df[result_df["Survey_ID"] == "test_survey_001"]
        assert len(survey_001) == 1
        assert abs(survey_001.iloc[0]["Herbivore Density"] - 50.0) < 0.01

        # test_survey_002: Sea Urchins - Diadema (45) over 1 dive -> density = 45
        survey_002 = result_df[result_df["Survey_ID"] == "test_survey_002"]
        assert len(survey_002) == 1
        assert abs(survey_002.iloc[0]["Herbivore Density"] - 45.0) < 0.01

        # test_survey_003: Sea Urchins - Diadema (30) over 1 dive -> density = 30
        survey_003 = result_df[result_df["Survey_ID"] == "test_survey_003"]
        assert len(survey_003) == 1
        assert abs(survey_003.iloc[0]["Herbivore Density"] - 30.0) < 0.01

    def test_inverts_carnivore_density_calculation(
        self,
        preprocessed_invert_data,
        invert_dive_numbers,
        redirect_constants_to_test_data,
    ):
        """Test that carnivore density is calculated correctly per survey."""
        daily_df = create_daily_df(preprocessed_invert_data, "inverts")
        daily_df = add_periods(daily_df, "seasonal")
        result_df = calculate_carnivore_density(
            daily_df, invert_dive_numbers, "inverts"
        )

        # Verify structure
        assert "Carnivore Density" in result_df.columns
        assert "Survey_ID" in result_df.columns

        # Test specific values
        # test_survey_001: Gastropods - Cone (5) over 1 dive -> density = 5
        survey_001 = result_df[result_df["Survey_ID"] == "test_survey_001"]
        assert len(survey_001) == 1
        assert abs(survey_001.iloc[0]["Carnivore Density"] - 5.0) < 0.01

        # test_survey_002: Sea Stars - Crown of Thorns (2) over 1 dive -> density = 2
        survey_002 = result_df[result_df["Survey_ID"] == "test_survey_002"]
        assert len(survey_002) == 1
        assert abs(survey_002.iloc[0]["Carnivore Density"] - 2.0) < 0.01

        # test_survey_003: No carnivores -> not in results (treated as 0)
        survey_003 = result_df[result_df["Survey_ID"] == "test_survey_003"]
        assert len(survey_003) == 0  # No row when density is 0

    def test_inverts_omnivore_density_calculation(
        self,
        preprocessed_invert_data,
        invert_dive_numbers,
        redirect_constants_to_test_data,
    ):
        """Test that omnivore density is calculated correctly per survey."""
        daily_df = create_daily_df(preprocessed_invert_data, "inverts")
        daily_df = add_periods(daily_df, "seasonal")
        result_df = calculate_omnivore_density(daily_df, invert_dive_numbers, "inverts")

        # Verify structure
        assert "Omnivore Density" in result_df.columns
        assert "Survey_ID" in result_df.columns

        # Test specific values
        # test_survey_001: Sea Cucumbers - Other (8) over 1 dive -> density = 8
        survey_001 = result_df[result_df["Survey_ID"] == "test_survey_001"]
        assert len(survey_001) == 1
        assert abs(survey_001.iloc[0]["Omnivore Density"] - 8.0) < 0.01

        # test_survey_002: No omnivores -> not in results (treated as 0)
        survey_002 = result_df[result_df["Survey_ID"] == "test_survey_002"]
        assert len(survey_002) == 0  # No row when density is 0

        # test_survey_003: Sea Cucumbers - Other (10) over 1 dive -> density = 10
        survey_003 = result_df[result_df["Survey_ID"] == "test_survey_003"]
        assert len(survey_003) == 1
        assert abs(survey_003.iloc[0]["Omnivore Density"] - 10.0) < 0.01

    def test_inverts_detritivore_density_calculation(
        self,
        preprocessed_invert_data,
        invert_dive_numbers,
        redirect_constants_to_test_data,
    ):
        """Test that detritivore density is calculated correctly per survey."""
        daily_df = create_daily_df(preprocessed_invert_data, "inverts")
        daily_df = add_periods(daily_df, "seasonal")
        result_df = calculate_detritivore_density(
            daily_df, invert_dive_numbers, "inverts"
        )

        # Verify structure
        assert "Detritivore Density" in result_df.columns
        assert "Survey_ID" in result_df.columns

        # Test specific values
        # test_survey_001: Bivalves - Giant Clam (3) over 1 dive -> density = 3
        survey_001 = result_df[result_df["Survey_ID"] == "test_survey_001"]
        assert len(survey_001) == 1
        assert abs(survey_001.iloc[0]["Detritivore Density"] - 3.0) < 0.01

        # test_survey_002: No detritivores -> not in results (treated as 0)
        survey_002 = result_df[result_df["Survey_ID"] == "test_survey_002"]
        assert len(survey_002) == 0  # No row when density is 0

        # test_survey_003: Bivalves - Giant Clam (5) over 1 dive -> density = 5
        survey_003 = result_df[result_df["Survey_ID"] == "test_survey_003"]
        assert len(survey_003) == 1
        assert abs(survey_003.iloc[0]["Detritivore Density"] - 5.0) < 0.01

    def test_inverts_corallivore_density_calculation(
        self,
        preprocessed_invert_data,
        invert_dive_numbers,
        redirect_constants_to_test_data,
    ):
        """Test that corallivore density is calculated correctly per survey."""
        daily_df = create_daily_df(preprocessed_invert_data, "inverts")
        daily_df = add_periods(daily_df, "seasonal")
        result_df = calculate_corallivore_density(
            daily_df, invert_dive_numbers, "inverts"
        )

        # Verify structure
        assert "Corallivore Density" in result_df.columns
        assert "Survey_ID" in result_df.columns

        # Test specific values
        # test_survey_001: No corallivores -> not in results (treated as 0)
        survey_001 = result_df[result_df["Survey_ID"] == "test_survey_001"]
        assert len(survey_001) == 0  # No row when density is 0

        # test_survey_002: Gastropods - Tiger Cowrie (6) over 1 dive -> density = 6
        survey_002 = result_df[result_df["Survey_ID"] == "test_survey_002"]
        assert len(survey_002) == 1
        assert abs(survey_002.iloc[0]["Corallivore Density"] - 6.0) < 0.01

        # test_survey_003: No corallivores -> not in results (treated as 0)
        survey_003 = result_df[result_df["Survey_ID"] == "test_survey_003"]
        assert len(survey_003) == 0  # No row when density is 0

    def test_species_not_in_any_trophic_group(
        self,
        preprocessed_invert_data,
        invert_dive_numbers,
        redirect_constants_to_test_data,
    ):
        """Test that species not found in any trophic group CSV raise an error."""
        # Create a modified dataset with a species that doesn't exist in any CSV
        modified_data = preprocessed_invert_data.copy()
        # Add a fake species row
        new_row = modified_data.iloc[0].copy()
        new_row["Species"] = "Unknown Invert Species"
        new_row["Total"] = 100
        modified_data = pd.concat(
            [modified_data, pd.DataFrame([new_row])], ignore_index=True
        )

        # Should raise ValueError when trying to calculate metrics with unknown species
        with pytest.raises(ValueError, match="not found in any trophic group CSV"):
            calculate_inverts_metrics(
                modified_data, invert_dive_numbers, "seasonal", include_biomass=False
            )


class TestSpeciesRichness:
    """Test species richness calculations."""

    def test_species_richness_calculation(
        self, preprocessed_invert_data, invert_dive_numbers
    ):
        """Test that species richness is calculated correctly per site."""
        daily_df = create_daily_df(preprocessed_invert_data, "inverts")

        result_df = calculate_species_richness(daily_df, invert_dive_numbers)

        # Check that result is a DataFrame
        assert isinstance(result_df, pd.DataFrame)

        # Check expected columns
        assert "Site" in result_df.columns
        assert "Species Richness" in result_df.columns
        assert "Average Species Richness" in result_df.columns
        assert "Number of Surveys" in result_df.columns

        # Check that we have results for both sites
        assert len(result_df) == 2
        sites = result_df["Site"].tolist()
        assert "Test Site A" in sites
        assert "Test Site B" in sites

    def test_species_richness_values(
        self, preprocessed_invert_data, invert_dive_numbers
    ):
        """Test that species richness values are correct."""
        daily_df = create_daily_df(preprocessed_invert_data, "inverts")
        result_df = calculate_species_richness(daily_df, invert_dive_numbers)

        # For Test Site A:
        # Survey 1: Sea Urchins - Diadema, Gastropods - Cone, Bivalves - Giant Clam, Sea Cucumbers - Other (4 species)
        # Survey 2: Sea Urchins - Diadema, Gastropods - Cone, Sea Stars - Crown of Thorns (3 species)
        # Unique species total: 5 (all of the above)
        # Number of surveys: 2
        site_a_result = result_df[result_df["Site"] == "Test Site A"]
        assert len(site_a_result) == 1
        assert site_a_result.iloc[0]["Species Richness"] == 5
        assert site_a_result.iloc[0]["Number of Surveys"] == 2
        expected_avg = round(5 / 2, 2)
        assert (
            abs(site_a_result.iloc[0]["Average Species Richness"] - expected_avg) < 0.01
        )

        # For Test Site B:
        # Survey 3: Sea Urchins - Diadema, Bivalves - Giant Clam, Sea Cucumbers - Other (3 species)
        # Number of surveys: 1
        site_b_result = result_df[result_df["Site"] == "Test Site B"]
        assert len(site_b_result) == 1
        assert site_b_result.iloc[0]["Species Richness"] == 3
        assert site_b_result.iloc[0]["Number of Surveys"] == 1
        assert abs(site_b_result.iloc[0]["Average Species Richness"] - 3.0) < 0.01
