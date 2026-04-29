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
    calculate_commercial_count,
    calculate_commercial_biomass,
)
from fish_and_inverts_shared_metrics import (
    calculate_biomass,
    calculate_total_count,
    calculate_total_biomass,
    calculate_herbivore_count,
    calculate_carnivore_count,
    calculate_omnivore_count,
    calculate_detritivore_count,
    calculate_corallivore_count,
    calculate_species_richness,
)
from utils import prepare_survey_df


class TestFishBiomassCalculation:
    """Test biomass calculations for fish."""

    def test_biomass_calculation_values(
        self, preprocessed_fish_data, test_constants_dir
    ):
        """Test that biomass is calculated correctly using the formula."""
        survey_df = prepare_survey_df(preprocessed_fish_data, "fish", "seasonal")
        biomass_df = calculate_biomass(
            survey_df, str(test_constants_dir / "biomass_coeffs_fish.csv")
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

    def test_total_count_and_density(self, preprocessed_fish_data):
        """Test total count and density calculations."""
        survey_df = prepare_survey_df(preprocessed_fish_data, "fish", "seasonal")

        result_df = calculate_total_count(survey_df)

        # Check that the result has the expected columns
        assert "Total Count" in result_df.columns
        assert "Survey_ID" in result_df.columns
        assert "Site" in result_df.columns

        # For test_survey_001, total count = 5+10+3+20+2 = 40
        survey_001_result = result_df[result_df["Survey_ID"] == "test_survey_001"]
        assert len(survey_001_result) == 1
        assert abs(survey_001_result.iloc[0]["Total Count"] - 40.0) < 0.01


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
        self, preprocessed_fish_data, redirect_constants_to_test_data
    ):
        """Test that commercial fish density is calculated correctly per survey."""
        survey_df = prepare_survey_df(preprocessed_fish_data, "fish", "seasonal")
        result_df = calculate_commercial_count(survey_df)

        # Verify structure
        assert "Commercial Count" in result_df.columns
        assert "Survey_ID" in result_df.columns

        # Test specific values
        # test_survey_001: Parrotfish (5) + Surgeonfish (10) = 15
        survey_001 = result_df[result_df["Survey_ID"] == "test_survey_001"]
        assert len(survey_001) == 1
        assert abs(survey_001.iloc[0]["Commercial Count"] - 15.0) < 0.01

        # test_survey_002: Parrotfish (4) + Surgeonfish (8) + Fusilier (15) = 27
        survey_002 = result_df[result_df["Survey_ID"] == "test_survey_002"]
        assert len(survey_002) == 1
        assert abs(survey_002.iloc[0]["Commercial Count"] - 27.0) < 0.01

        # test_survey_003: Parrotfish (6)
        survey_003 = result_df[result_df["Survey_ID"] == "test_survey_003"]
        assert len(survey_003) == 1
        assert abs(survey_003.iloc[0]["Commercial Count"] - 6.0) < 0.01

    def test_commercial_biomass_calculation(
        self,
        preprocessed_fish_data,
        test_constants_dir,
        redirect_constants_to_test_data,
    ):
        """Test that commercial biomass is calculated correctly per survey."""
        survey_df = prepare_survey_df(preprocessed_fish_data, "fish", "seasonal")
        survey_df = calculate_biomass(
            survey_df, str(test_constants_dir / "biomass_coeffs_fish.csv")
        )
        result_df = calculate_commercial_biomass(survey_df)

        # Verify structure
        assert "Commercial Biomass" in result_df.columns
        assert "Survey_ID" in result_df.columns

        # Test specific values
        # test_survey_001:
        # - Parrotfish: 5 * 0.0206 * (15^2.949) ≈ 269.65 grams
        # - Surgeonfish: 10 * 0.0157 * (7.5^3.061) ≈ 46.62 grams
        # - Total: 316.27 grams = 0.31627 kg
        survey_001 = result_df[result_df["Survey_ID"] == "test_survey_001"]
        assert len(survey_001) == 1
        expected_biomass_001 = (
            5 * 0.0206 * (15**2.949) + 10 * 0.0157 * (7.5**3.061)
        ) / 1000  # Convert to kg
        assert (
            abs(survey_001.iloc[0]["Commercial Biomass"] - expected_biomass_001) < 0.01
        )

        # test_survey_002:
        # - Parrotfish: 4 * 0.0206 * (15^2.949) ≈ 215.72 grams
        # - Surgeonfish: 8 * 0.0157 * (7.5^3.061) ≈ 37.30 grams
        # - Fusilier: 15 * 0.0061 * (15^3.118) ≈ 279.14 grams
        # - Total: 532.16 grams = 0.53216 kg
        survey_002 = result_df[result_df["Survey_ID"] == "test_survey_002"]
        assert len(survey_002) == 1
        expected_biomass_002 = (
            4 * 0.0206 * (15**2.949)
            + 8 * 0.0157 * (7.5**3.061)
            + 15 * 0.0061 * (15**3.118)
        ) / 1000  # Convert to kg
        assert (
            abs(survey_002.iloc[0]["Commercial Biomass"] - expected_biomass_002) < 0.01
        )

        # test_survey_003:
        # - Parrotfish: 6 * 0.0206 * (7.5^2.949) ≈ 40.43 grams
        # - Total: 40.43 grams = 0.04043 kg
        survey_003 = result_df[result_df["Survey_ID"] == "test_survey_003"]
        assert len(survey_003) == 1
        expected_biomass_003 = (6 * 0.0206 * (7.5**2.949)) / 1000  # Convert to kg
        assert (
            abs(survey_003.iloc[0]["Commercial Biomass"] - expected_biomass_003) < 0.01
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
        self, preprocessed_fish_data, redirect_constants_to_test_data
    ):
        """Test that herbivore density is calculated correctly per survey."""
        survey_df = prepare_survey_df(preprocessed_fish_data, "fish", "seasonal")
        result_df = calculate_herbivore_count(survey_df, "fish")

        # Verify structure
        assert "Herbivore Count" in result_df.columns
        assert "Survey_ID" in result_df.columns

        # Test specific values
        # test_survey_001: Surgeonfish - Other (10)
        survey_001 = result_df[result_df["Survey_ID"] == "test_survey_001"]
        assert len(survey_001) == 1
        assert abs(survey_001.iloc[0]["Herbivore Count"] - 10.0) < 0.01

        # test_survey_002: Surgeonfish - Other (8) + Fusilier (15) = 23
        survey_002 = result_df[result_df["Survey_ID"] == "test_survey_002"]
        assert len(survey_002) == 1
        assert abs(survey_002.iloc[0]["Herbivore Count"] - 23.0) < 0.01

        # test_survey_003: No herbivores -> not in results (treated as 0)
        survey_003 = result_df[result_df["Survey_ID"] == "test_survey_003"]
        assert len(survey_003) == 0  # No row when density is 0

    def test_fish_carnivore_density_calculation(
        self, preprocessed_fish_data, redirect_constants_to_test_data
    ):
        """Test that carnivore density is calculated correctly per survey."""
        survey_df = prepare_survey_df(preprocessed_fish_data, "fish", "seasonal")
        result_df = calculate_carnivore_count(survey_df, "fish")

        # Verify structure
        assert "Carnivore Count" in result_df.columns
        assert "Survey_ID" in result_df.columns

        # Test specific values
        # test_survey_001: Grouper (2)
        survey_001 = result_df[result_df["Survey_ID"] == "test_survey_001"]
        assert len(survey_001) == 1
        assert abs(survey_001.iloc[0]["Carnivore Count"] - 2.0) < 0.01

        # test_survey_002: No carnivores -> not in results (treated as 0)
        survey_002 = result_df[result_df["Survey_ID"] == "test_survey_002"]
        assert len(survey_002) == 0  # No row when density is 0

        # test_survey_003: Grouper (3)
        survey_003 = result_df[result_df["Survey_ID"] == "test_survey_003"]
        assert len(survey_003) == 1
        assert abs(survey_003.iloc[0]["Carnivore Count"] - 3.0) < 0.01

    def test_fish_omnivore_density_calculation(
        self, preprocessed_fish_data, redirect_constants_to_test_data
    ):
        """Test that omnivore density is calculated correctly per survey."""
        survey_df = prepare_survey_df(preprocessed_fish_data, "fish", "seasonal")
        result_df = calculate_omnivore_count(survey_df, "fish")

        # Verify structure
        assert "Omnivore Count" in result_df.columns
        assert "Survey_ID" in result_df.columns

        # Test specific values
        # test_survey_001: Parrotfish - Other (5)
        survey_001 = result_df[result_df["Survey_ID"] == "test_survey_001"]
        assert len(survey_001) == 1
        assert abs(survey_001.iloc[0]["Omnivore Count"] - 5.0) < 0.01

        # test_survey_002: Parrotfish - Other (4)
        survey_002 = result_df[result_df["Survey_ID"] == "test_survey_002"]
        assert len(survey_002) == 1
        assert abs(survey_002.iloc[0]["Omnivore Count"] - 4.0) < 0.01

        # test_survey_003: Parrotfish - Other (6)
        survey_003 = result_df[result_df["Survey_ID"] == "test_survey_003"]
        assert len(survey_003) == 1
        assert abs(survey_003.iloc[0]["Omnivore Count"] - 6.0) < 0.01

    def test_fish_detritivore_density_calculation(
        self, preprocessed_fish_data, redirect_constants_to_test_data
    ):
        """Test that detritivore density is calculated correctly per survey."""
        survey_df = prepare_survey_df(preprocessed_fish_data, "fish", "seasonal")
        result_df = calculate_detritivore_count(survey_df, "fish")

        # Verify structure
        assert "Detritivore Count" in result_df.columns
        assert "Survey_ID" in result_df.columns

        # Test specific values
        # test_survey_001: Rabbitfish (3)
        survey_001 = result_df[result_df["Survey_ID"] == "test_survey_001"]
        assert len(survey_001) == 1
        assert abs(survey_001.iloc[0]["Detritivore Count"] - 3.0) < 0.01

        # test_survey_002: No detritivores -> not in results (treated as 0)
        survey_002 = result_df[result_df["Survey_ID"] == "test_survey_002"]
        assert len(survey_002) == 0  # No row when density is 0

        # test_survey_003: No detritivores -> not in results (treated as 0)
        survey_003 = result_df[result_df["Survey_ID"] == "test_survey_003"]
        assert len(survey_003) == 0  # No row when density is 0

    def test_fish_corallivore_density_calculation(
        self, preprocessed_fish_data, redirect_constants_to_test_data
    ):
        """Test that corallivore density is calculated correctly per survey."""
        survey_df = prepare_survey_df(preprocessed_fish_data, "fish", "seasonal")
        result_df = calculate_corallivore_count(survey_df, "fish")

        # Verify structure
        assert "Corallivore Count" in result_df.columns
        assert "Survey_ID" in result_df.columns

        # Test specific values
        # test_survey_001: Damselfish (20)
        survey_001 = result_df[result_df["Survey_ID"] == "test_survey_001"]
        assert len(survey_001) == 1
        assert abs(survey_001.iloc[0]["Corallivore Count"] - 20.0) < 0.01

        # test_survey_002: No corallivores -> not in results (treated as 0)
        survey_002 = result_df[result_df["Survey_ID"] == "test_survey_002"]
        assert len(survey_002) == 0  # No row when density is 0

        # test_survey_003: Damselfish (25)
        survey_003 = result_df[result_df["Survey_ID"] == "test_survey_003"]
        assert len(survey_003) == 1
        assert abs(survey_003.iloc[0]["Corallivore Count"] - 25.0) < 0.01

    def test_species_not_in_any_trophic_group(
        self, preprocessed_fish_data, redirect_constants_to_test_data
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
            calculate_fish_metrics(modified_data, "seasonal")


class TestSpeciesRichness:
    """Test species richness calculations."""

    def test_species_richness_run(self, preprocessed_fish_data):
        """Test that species richness returns dataframe with correct columns and sites."""
        survey_df = prepare_survey_df(preprocessed_fish_data, "fish", "seasonal")
        result_df = calculate_species_richness(survey_df)

        # Check that result is a DataFrame
        assert isinstance(result_df, pd.DataFrame)

        # Check expected columns
        assert "Period" in result_df.columns
        assert "Site" in result_df.columns
        assert "Species Richness" in result_df.columns
        assert "Average Species Richness" in result_df.columns
        assert "Number of Surveys" in result_df.columns
        assert "Species Richness Shallow" in result_df.columns
        assert "Average Species Richness Shallow" in result_df.columns
        assert "Number of Surveys Shallow" in result_df.columns
        assert "Species Richness Medium" in result_df.columns
        assert "Average Species Richness Medium" in result_df.columns
        assert "Number of Surveys Medium" in result_df.columns
        assert "Species Richness Deep" in result_df.columns
        assert "Average Species Richness Deep" in result_df.columns
        assert "Number of Surveys Deep" in result_df.columns
        assert "Number of Surveys" in result_df.columns

        # Check that we have results for each site (both sites are in the same period)
        assert len(result_df) == 2

        # Check that only the two expected sites are in the results
        sites = result_df["Site"].tolist()
        assert "Test Site A" in sites
        assert "Test Site B" in sites

    def test_species_richness_overall_calculation(self, preprocessed_fish_data):
        """Test that species richness values are correct."""
        survey_df = prepare_survey_df(preprocessed_fish_data, "fish", "seasonal")
        result_df = calculate_species_richness(survey_df)

        # For Test Site A:
        # Survey 1 (Medium): Parrotfish - Other, Surgeonfish - Other, Rabbitfish, Damselfish, Grouper (5 species)
        # Survey 2 (Shallow): Parrotfish - Other, Surgeonfish - Other, Fusilier (3 species)
        # Survey 4 (Medium): Fusilier (1 species)
        # Unique species total: 6 (Parrotfish, Surgeonfish, Rabbitfish, Damselfish, Grouper, Fusilier)
        # Number of surveys: 3
        # Average: 6/3 = 2.0
        site_a_result = result_df[result_df["Site"] == "Test Site A"]
        assert len(site_a_result) == 1
        assert site_a_result.iloc[0]["Species Richness"] == 6
        assert site_a_result.iloc[0]["Number of Surveys"] == 3
        assert site_a_result.iloc[0]["Average Species Richness"] == 2.0

        # For Test Site B:
        # Survey 3 (Deep): Grouper, Damselfish, Parrotfish - Other
        # Unique species total: 3
        # Number of surveys: 1
        # Average: 3/1 = 3.0
        site_b_result = result_df[result_df["Site"] == "Test Site B"]
        assert len(site_b_result) == 1
        assert site_b_result.iloc[0]["Species Richness"] == 3
        assert site_b_result.iloc[0]["Number of Surveys"] == 1
        assert site_b_result.iloc[0]["Average Species Richness"] == 3.0

    def test_species_richness_shallow_depth(self, preprocessed_fish_data):
        """Test that Shallow depth species richness values are correct."""
        survey_df = prepare_survey_df(preprocessed_fish_data, "fish", "seasonal")
        result_df = calculate_species_richness(survey_df)

        # Test Site A: test_survey_002 is at Shallow depth with 3 species
        # Species: Parrotfish - Other, Surgeonfish - Other, Fusilier
        site_a_result = result_df[result_df["Site"] == "Test Site A"]
        assert len(site_a_result) == 1
        assert site_a_result.iloc[0]["Species Richness Shallow"] == 3
        assert site_a_result.iloc[0]["Number of Surveys Shallow"] == 1
        assert site_a_result.iloc[0]["Average Species Richness Shallow"] == 3.0

        # Test Site B: no Shallow surveys
        site_b_result = result_df[result_df["Site"] == "Test Site B"]
        assert len(site_b_result) == 1
        assert pd.isna(site_b_result.iloc[0]["Species Richness Shallow"])
        assert pd.isna(site_b_result.iloc[0]["Number of Surveys Shallow"])
        assert pd.isna(site_b_result.iloc[0]["Average Species Richness Shallow"])

    def test_species_richness_medium_depth(self, preprocessed_fish_data):
        """Test that Medium depth species richness values are correct."""
        survey_df = prepare_survey_df(preprocessed_fish_data, "fish", "seasonal")
        result_df = calculate_species_richness(survey_df)

        # Test Site A: test_survey_001 and test_survey_004 are at Medium depth
        # test_survey_001 species: 5 species (Parrotfish, Surgeonfish, Rabbitfish, Damselfish, Grouper)
        # test_survey_004 species: 1 species (Fusilier)
        # Unique species across both Medium surveys: 6
        # Number of surveys: 2
        # Average: 6/2 = 3.0
        site_a_result = result_df[result_df["Site"] == "Test Site A"]
        assert len(site_a_result) == 1
        assert site_a_result.iloc[0]["Species Richness Medium"] == 6
        assert site_a_result.iloc[0]["Number of Surveys Medium"] == 2
        assert site_a_result.iloc[0]["Average Species Richness Medium"] == 3.0

        # Test Site B: no Medium surveys
        site_b_result = result_df[result_df["Site"] == "Test Site B"]
        assert len(site_b_result) == 1
        assert pd.isna(site_b_result.iloc[0]["Species Richness Medium"])
        assert pd.isna(site_b_result.iloc[0]["Number of Surveys Medium"])
        assert pd.isna(site_b_result.iloc[0]["Average Species Richness Medium"])

    def test_species_richness_deep_depth(self, preprocessed_fish_data):
        """Test that Deep depth species richness values are correct."""
        survey_df = prepare_survey_df(preprocessed_fish_data, "fish", "seasonal")
        result_df = calculate_species_richness(survey_df)

        # Test Site A: no Deep surveys
        site_a_result = result_df[result_df["Site"] == "Test Site A"]
        assert len(site_a_result) == 1
        assert pd.isna(site_a_result.iloc[0]["Species Richness Deep"])
        assert pd.isna(site_a_result.iloc[0]["Number of Surveys Deep"])
        assert pd.isna(site_a_result.iloc[0]["Average Species Richness Deep"])

        # Test Site B: test_survey_003 is at Deep depth with 3 species
        # Species: Grouper, Damselfish, Parrotfish - Other
        site_b_result = result_df[result_df["Site"] == "Test Site B"]
        assert len(site_b_result) == 1
        assert site_b_result.iloc[0]["Species Richness Deep"] == 3
        assert site_b_result.iloc[0]["Number of Surveys Deep"] == 1
        assert site_b_result.iloc[0]["Average Species Richness Deep"] == 3.0
