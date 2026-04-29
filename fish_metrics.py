import pandas as pd
from fish_and_inverts_shared_metrics import (
    calculate_biomass,
    calculate_carnivore_count,
    calculate_corallivore_count,
    calculate_detritivore_count,
    calculate_herbivore_count,
    calculate_omnivore_count,
    calculate_total_biomass,
    calculate_total_count,
    validate_species_in_trophic_groups,
)
from utils import create_survey_df, summarize_with_ci


def calculate_fish_metrics(
    pre_processed_fish_data_df: pd.DataFrame,
    period: str,
) -> pd.DataFrame:
    """
    Calculate fish metrics for each Survey_ID before summarizing by season.
    """
    survey_df = create_survey_df(pre_processed_fish_data_df, "fish", period)

    # Validate that all species in trophic groups are in the fish data
    validate_species_in_trophic_groups(survey_df, "fish")

    survey_df = calculate_biomass(survey_df, "data/constants/biomass_coeffs_fish.csv")

    base_survey = survey_df[["Survey_ID", "Date", "Site", "Period"]].drop_duplicates()

    metric_frames = [
        calculate_total_count(survey_df),
        calculate_commercial_count(survey_df),
        calculate_total_biomass(survey_df),
        calculate_commercial_biomass(survey_df),
        calculate_herbivore_count(survey_df, "fish"),
        calculate_carnivore_count(survey_df, "fish"),
        calculate_omnivore_count(survey_df, "fish"),
        calculate_detritivore_count(survey_df, "fish"),
        calculate_corallivore_count(survey_df, "fish"),
    ]

    survey_results_df = base_survey.copy()
    for frame in metric_frames:
        survey_results_df = survey_results_df.merge(
            frame, on=["Survey_ID", "Date", "Period", "Site"], how="left"
        )

    # Define mapping from count columns to density columns
    metric_mapping = {
        "Corallivore Count": "Corallivore Density",
        "Detritivore Count": "Detritivore Density",
        "Omnivore Count": "Omnivore Density",
        "Carnivore Count": "Carnivore Density",
        "Herbivore Count": "Herbivore Density",
        "Total Count": "Total Density",
        "Total Biomass": "Total Biomass Density",
        "Commercial Count": "Commercial Density",
        "Commercial Biomass": "Commercial Biomass Density",
    }

    count_columns = list(metric_mapping.keys())
    # Fill NaN values in count columns with 0
    for column in count_columns:
        if column in survey_results_df.columns:
            survey_results_df[column] = survey_results_df[column].fillna(0)
        # else add a column with 0 values
        else:
            survey_results_df[column] = 0

    # Create density columns from count columns (counts are per dive)
    for count_col, density_col in metric_mapping.items():
        if count_col in survey_results_df.columns:
            survey_results_df[density_col] = survey_results_df[count_col]

    # Calculate densities and their statistics for final output
    density_columns = list(metric_mapping.values())
    value_cols = [c for c in density_columns if c in survey_results_df.columns]

    seasonal_summary_df = summarize_with_ci(
        survey_results_df,
        group_cols=["Period", "Site"],
        value_cols=value_cols,
    )

    return seasonal_summary_df


def calculate_commercial_count(
    survey_df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Calculate survey-level commercial fish counts before seasonal summarization.
    """
    commercial_fish_names = (
        pd.read_csv("data/constants/commercial_fish.csv", header=None)
        .iloc[:, 0]
        .tolist()
    )
    commercial_count = (
        survey_df[survey_df["Species"].isin(commercial_fish_names)]
        .groupby(["Survey_ID", "Date", "Period", "Site"])["Total"]
        .sum()
        .reset_index()
        .rename(columns={"Total": "Commercial Count"})
    )

    return commercial_count[["Survey_ID", "Date", "Period", "Site", "Commercial Count"]]


def calculate_commercial_biomass(survey_df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate survey-level commercial biomass before seasonal summarization.
    """
    commercial_fish_names = (
        pd.read_csv("data/constants/commercial_fish.csv", header=None)
        .iloc[:, 0]
        .tolist()
    )
    commercial_biomass = (
        survey_df[survey_df["Species"].isin(commercial_fish_names)]
        .groupby(["Survey_ID", "Date", "Period", "Site"])["Total Biomass"]
        .sum()
        .reset_index()
        .rename(columns={"Total Biomass": "Commercial Biomass"})
    )

    commercial_biomass["Commercial Biomass"] = (
        commercial_biomass["Commercial Biomass"] / 1000
    )  # Convert to kg

    return commercial_biomass[
        ["Survey_ID", "Date", "Period", "Site", "Commercial Biomass"]
    ]
