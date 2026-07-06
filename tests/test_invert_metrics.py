"""
Tests for invertebrate metrics calculations.
"""

import sys
from pathlib import Path

import pandas as pd
import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from invert_metrics import calculate_inverts_metrics
from fish_and_inverts_shared_metrics import (
    calculate_biomass,
    calculate_total_count,
    calculate_herbivore_count,
    calculate_carnivore_count,
    calculate_omnivore_count,
    calculate_detritivore_count,
    calculate_corallivore_count,
    calculate_species_richness,
)
from utils import prepare_survey_df


class TestInvertBiomassCalculation:
    """Test biomass calculations for invertebrates."""

    def test_biomass_calculation_values(
        self, preprocessed_invert_data, test_constants_dir
    ):
        """Test that biomass is calculated correctly for invertebrates."""
        survey_df = prepare_survey_df(preprocessed_invert_data, "inverts", "seasonal")
        biomass_df = calculate_biomass(
            survey_df, str(test_constants_dir / "biomass_coeffs_inverts.csv")
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

    def test_total_count_and_density(self, preprocessed_invert_data):
        """Test total count and density calculations."""
        survey_df = prepare_survey_df(preprocessed_invert_data, "inverts", "seasonal")

        result_df = calculate_total_count(survey_df)

        # Check that the result has the expected columns
        assert "Total Count" in result_df.columns
        assert "Survey_ID" in result_df.columns
        assert "Site" in result_df.columns

        # For test_survey_001, total count = 50+5+3+8 = 66
        survey_001_result = result_df[result_df["Survey_ID"] == "test_survey_001"]
        assert len(survey_001_result) == 1
        assert abs(survey_001_result.iloc[0]["Total Count"] - 66.0) < 0.01


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

    def test_inverts_herbivore_count_calculation(
        self,
        preprocessed_invert_data,
        redirect_constants_to_test_data,
    ):
        """Test that herbivore count is calculated correctly per survey."""
        survey_df = prepare_survey_df(preprocessed_invert_data, "inverts", "seasonal")
        result_df = calculate_herbivore_count(survey_df, "inverts")

        # Verify structure
        assert "Herbivore Count" in result_df.columns
        assert "Survey_ID" in result_df.columns

        # Test specific values
        # test_survey_001: Sea Urchins - Diadema (50)
        survey_001 = result_df[result_df["Survey_ID"] == "test_survey_001"]
        assert len(survey_001) == 1
        assert abs(survey_001.iloc[0]["Herbivore Count"] - 50.0) < 0.01

        # test_survey_002: Sea Urchins - Diadema (45)
        survey_002 = result_df[result_df["Survey_ID"] == "test_survey_002"]
        assert len(survey_002) == 1
        assert abs(survey_002.iloc[0]["Herbivore Count"] - 45.0) < 0.01

        # test_survey_003: Sea Urchins - Diadema (30)
        survey_003 = result_df[result_df["Survey_ID"] == "test_survey_003"]
        assert len(survey_003) == 1
        assert abs(survey_003.iloc[0]["Herbivore Count"] - 30.0) < 0.01

        # test_survey_004: Sea Urchins - Diadema (10)
        survey_004 = result_df[result_df["Survey_ID"] == "test_survey_004"]
        assert len(survey_004) == 1
        assert abs(survey_004.iloc[0]["Herbivore Count"] - 10.0) < 0.01

    def test_inverts_carnivore_count_calculation(
        self,
        preprocessed_invert_data,
        redirect_constants_to_test_data,
    ):
        """Test that carnivore count is calculated correctly per survey."""
        survey_df = prepare_survey_df(preprocessed_invert_data, "inverts", "seasonal")
        result_df = calculate_carnivore_count(survey_df, "inverts")

        # Verify structure
        assert "Carnivore Count" in result_df.columns
        assert "Survey_ID" in result_df.columns

        # Test specific values
        # test_survey_001: Gastropods - Cone (5)
        survey_001 = result_df[result_df["Survey_ID"] == "test_survey_001"]
        assert len(survey_001) == 1
        assert abs(survey_001.iloc[0]["Carnivore Count"] - 5.0) < 0.01

        # test_survey_002: Sea Stars - Crown of Thorns (2)
        survey_002 = result_df[result_df["Survey_ID"] == "test_survey_002"]
        assert len(survey_002) == 1
        assert abs(survey_002.iloc[0]["Carnivore Count"] - 2.0) < 0.01

        # test_survey_003: No carnivores -> not in results (treated as 0)
        survey_003 = result_df[result_df["Survey_ID"] == "test_survey_003"]
        assert len(survey_003) == 0  # No row when count is 0

        # test_survey_004: No carnivores -> not in results (treated as 0)
        survey_004 = result_df[result_df["Survey_ID"] == "test_survey_004"]
        assert len(survey_004) == 0  # No row when count is 0

    def test_inverts_omnivore_count_calculation(
        self,
        preprocessed_invert_data,
        redirect_constants_to_test_data,
    ):
        """Test that omnivore count is calculated correctly per survey."""
        survey_df = prepare_survey_df(preprocessed_invert_data, "inverts", "seasonal")
        result_df = calculate_omnivore_count(survey_df, "inverts")

        # Verify structure
        assert "Omnivore Count" in result_df.columns
        assert "Survey_ID" in result_df.columns

        # Test specific values
        # test_survey_001: Sea Cucumbers - Other (8)
        survey_001 = result_df[result_df["Survey_ID"] == "test_survey_001"]
        assert len(survey_001) == 1
        assert abs(survey_001.iloc[0]["Omnivore Count"] - 8.0) < 0.01

        # test_survey_002: No omnivores -> not in results (treated as 0)
        survey_002 = result_df[result_df["Survey_ID"] == "test_survey_002"]
        assert len(survey_002) == 0  # No row when count is 0

        # test_survey_003: Sea Cucumbers - Other (10)
        survey_003 = result_df[result_df["Survey_ID"] == "test_survey_003"]
        assert len(survey_003) == 1
        assert abs(survey_003.iloc[0]["Omnivore Count"] - 10.0) < 0.01

        # test_survey_004: No omnivores -> not in results (treated as 0)
        survey_004 = result_df[result_df["Survey_ID"] == "test_survey_004"]
        assert len(survey_004) == 0  # No row when count is 0

    def test_inverts_detritivore_count_calculation(
        self,
        preprocessed_invert_data,
        redirect_constants_to_test_data,
    ):
        """Test that detritivore count is calculated correctly per survey."""
        survey_df = prepare_survey_df(preprocessed_invert_data, "inverts", "seasonal")
        result_df = calculate_detritivore_count(survey_df, "inverts")

        # Verify structure
        assert "Detritivore Count" in result_df.columns
        assert "Survey_ID" in result_df.columns

        # Test specific values
        # test_survey_001: Bivalves - Giant Clam (3)
        survey_001 = result_df[result_df["Survey_ID"] == "test_survey_001"]
        assert len(survey_001) == 1
        assert abs(survey_001.iloc[0]["Detritivore Count"] - 3.0) < 0.01

        # test_survey_002: No detritivores -> not in results (treated as 0)
        survey_002 = result_df[result_df["Survey_ID"] == "test_survey_002"]
        assert len(survey_002) == 0  # No row when count is 0

        # test_survey_003: Bivalves - Giant Clam (5)
        survey_003 = result_df[result_df["Survey_ID"] == "test_survey_003"]
        assert len(survey_003) == 1
        assert abs(survey_003.iloc[0]["Detritivore Count"] - 5.0) < 0.01

        # test_survey_004: No detritivores -> not in results (treated as 0)
        survey_004 = result_df[result_df["Survey_ID"] == "test_survey_004"]
        assert len(survey_004) == 0  # No row when count is 0

    def test_inverts_corallivore_count_calculation(
        self,
        preprocessed_invert_data,
        redirect_constants_to_test_data,
    ):
        """Test that corallivore count is calculated correctly per survey."""
        survey_df = prepare_survey_df(preprocessed_invert_data, "inverts", "seasonal")
        result_df = calculate_corallivore_count(survey_df, "inverts")

        # Verify structure
        assert "Corallivore Count" in result_df.columns
        assert "Survey_ID" in result_df.columns

        # Test specific values
        # test_survey_001: No corallivores -> not in results (treated as 0)
        survey_001 = result_df[result_df["Survey_ID"] == "test_survey_001"]
        assert len(survey_001) == 0  # No row when count is 0

        # test_survey_002: Gastropods - Tiger Cowrie (6)
        survey_002 = result_df[result_df["Survey_ID"] == "test_survey_002"]
        assert len(survey_002) == 1
        assert abs(survey_002.iloc[0]["Corallivore Count"] - 6.0) < 0.01

        # test_survey_003: No corallivores -> not in results (treated as 0)
        survey_003 = result_df[result_df["Survey_ID"] == "test_survey_003"]
        assert len(survey_003) == 0  # No row when count is 0

        # test_survey_004: No corallivores -> not in results (treated as 0)
        survey_004 = result_df[result_df["Survey_ID"] == "test_survey_004"]
        assert len(survey_004) == 0  # No row when count is 0

    def test_species_not_in_any_trophic_group(
        self,
        preprocessed_invert_data,
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
            calculate_inverts_metrics(modified_data, "seasonal", include_biomass=False)


class TestSpeciesRichness:
    """Test species richness calculations."""

    def test_species_richness_run(self, preprocessed_invert_data):
        """Test that species richness returns dataframe with correct columns and sites."""
        survey_df = prepare_survey_df(preprocessed_invert_data, "inverts", "seasonal")
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

    def test_species_richness_overall_calculation(self, preprocessed_invert_data):
        """Test that species richness values are correct."""
        survey_df = prepare_survey_df(preprocessed_invert_data, "inverts", "seasonal")
        result_df = calculate_species_richness(survey_df)

        # For Test Site A:
        # Survey 1 (Shallow): Sea Urchins - Diadema, Gastropods - Cone, Bivalves - Giant Clam, Sea Cucumbers - Other
        # Survey 2 (Medium): Sea Urchins - Diadema, Gastropods - Tiger Cowrie, Sea Stars - Crown of Thorns
        # Survey 4 (Shallow): Sea Urchins - Diadema
        # Unique species total: 6
        # Number of surveys: 3
        site_a_result = result_df[result_df["Site"] == "Test Site A"]
        assert len(site_a_result) == 1
        assert site_a_result.iloc[0]["Species Richness"] == 6
        assert site_a_result.iloc[0]["Number of Surveys"] == 3
        assert site_a_result.iloc[0]["Average Species Richness"] == 2.0

        # For Test Site B:
        # Survey 3: Sea Urchins - Diadema, Bivalves - Giant Clam, Sea Cucumbers - Other
        # Unique species total: 3
        # Number of surveys: 1
        site_b_result = result_df[result_df["Site"] == "Test Site B"]
        assert len(site_b_result) == 1
        assert site_b_result.iloc[0]["Species Richness"] == 3
        assert site_b_result.iloc[0]["Number of Surveys"] == 1

    def test_species_richness_shallow_depth(self, preprocessed_invert_data):
        """Test that Shallow depth species richness values are correct."""
        survey_df = prepare_survey_df(preprocessed_invert_data, "inverts", "seasonal")
        result_df = calculate_species_richness(survey_df)

        # Test Site A: test_survey_001 and test_survey_004 are at Shallow depth
        # test_survey_001 species: Sea Urchins - Diadema, Gastropods - Cone, Bivalves - Giant Clam, Sea Cucumbers - Other
        # test_survey_004 species: Sea Urchins - Diadema
        # Unique species across both Shallow surveys: 4
        # Number of surveys: 2
        site_a_result = result_df[result_df["Site"] == "Test Site A"]
        assert len(site_a_result) == 1
        assert site_a_result.iloc[0]["Species Richness Shallow"] == 4
        assert site_a_result.iloc[0]["Number of Surveys Shallow"] == 2
        assert site_a_result.iloc[0]["Average Species Richness Shallow"] == 2.0

        # Test Site B: no Shallow surveys
        site_b_result = result_df[result_df["Site"] == "Test Site B"]
        assert len(site_b_result) == 1
        assert pd.isna(site_b_result.iloc[0]["Species Richness Shallow"])
        assert pd.isna(site_b_result.iloc[0]["Number of Surveys Shallow"])
        assert pd.isna(site_b_result.iloc[0]["Average Species Richness Shallow"])

    def test_species_richness_medium_depth(self, preprocessed_invert_data):
        """Test that Medium depth species richness values are correct."""
        survey_df = prepare_survey_df(preprocessed_invert_data, "inverts", "seasonal")
        result_df = calculate_species_richness(survey_df)

        # Test Site A: test_survey_002 is at Medium depth with 3 species
        # Species: Sea Urchins - Diadema, Gastropods - Tiger Cowrie, Sea Stars - Crown of Thorns
        site_a_result = result_df[result_df["Site"] == "Test Site A"]
        assert len(site_a_result) == 1
        assert site_a_result.iloc[0]["Species Richness Medium"] == 3
        assert site_a_result.iloc[0]["Number of Surveys Medium"] == 1
        assert site_a_result.iloc[0]["Average Species Richness Medium"] == 3.0

        # Test Site B: no Medium surveys
        site_b_result = result_df[result_df["Site"] == "Test Site B"]
        assert len(site_b_result) == 1
        assert pd.isna(site_b_result.iloc[0]["Species Richness Medium"])
        assert pd.isna(site_b_result.iloc[0]["Number of Surveys Medium"])
        assert pd.isna(site_b_result.iloc[0]["Average Species Richness Medium"])

    def test_species_richness_deep_depth(self, preprocessed_invert_data):
        """Test that Deep depth species richness values are correct."""
        survey_df = prepare_survey_df(preprocessed_invert_data, "inverts", "seasonal")
        result_df = calculate_species_richness(survey_df)

        # Test Site A: no Deep surveys
        site_a_result = result_df[result_df["Site"] == "Test Site A"]
        assert len(site_a_result) == 1
        assert pd.isna(site_a_result.iloc[0]["Species Richness Deep"])
        assert pd.isna(site_a_result.iloc[0]["Number of Surveys Deep"])
        assert pd.isna(site_a_result.iloc[0]["Average Species Richness Deep"])

        # Test Site B: test_survey_003 is at Deep depth with 3 species
        # Species: Sea Urchins - Diadema, Bivalves - Giant Clam, Sea Cucumbers - Other
        site_b_result = result_df[result_df["Site"] == "Test Site B"]
        assert len(site_b_result) == 1
        assert site_b_result.iloc[0]["Species Richness Deep"] == 3
        assert site_b_result.iloc[0]["Number of Surveys Deep"] == 1
        assert site_b_result.iloc[0]["Average Species Richness Deep"] == 3.0
