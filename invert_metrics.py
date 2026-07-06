import pandas as pd
from fish_and_inverts_shared_metrics import (
    calculate_biomass,
    calculate_carnivore_count,
    calculate_corallivore_count,
    calculate_detritivore_count,
    calculate_herbivore_count,
    calculate_omnivore_count,
    calculate_species_richness,
    calculate_total_biomass,
    calculate_total_count,
    validate_species_in_trophic_groups,
)
from utils import prepare_survey_df
from statistics import summarize_with_ci


def calculate_inverts_metrics(
    pre_processed_inverts_data_df: pd.DataFrame,
    period: str,
    include_biomass: bool,
) -> pd.DataFrame:
    """
    Calculate invert metrics for each Date/Period/Site before summarizing by season.
    """
    survey_df = prepare_survey_df(pre_processed_inverts_data_df, "inverts", period)

    # Validate that all species are in at least one trophic group
    validate_species_in_trophic_groups(survey_df, "inverts")

    if include_biomass:
        survey_df = calculate_biomass(
            survey_df, "data/constants/biomass_coeffs_inverts.csv"
        )

    base_survey = survey_df[["Survey_ID", "Date", "Period", "Site"]].drop_duplicates()

    metric_frames = [
        calculate_total_count(survey_df),
        calculate_herbivore_count(survey_df, "inverts"),
        calculate_carnivore_count(survey_df, "inverts"),
        calculate_omnivore_count(survey_df, "inverts"),
        calculate_detritivore_count(survey_df, "inverts"),
        calculate_corallivore_count(survey_df, "inverts"),
    ]

    if include_biomass:
        metric_frames.append(calculate_total_biomass(survey_df))

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
    }
    if include_biomass:
        metric_mapping["Total Biomass"] = "Total Biomass Density"

    # Fill NaN values in count columns with 0
    count_columns = list(metric_mapping.keys())
    for column in count_columns:
        if column in survey_results_df.columns:
            survey_results_df[column] = survey_results_df[column].fillna(0)

    # Create density columns from count columns (counts are already per dive since dive numbers are all 1)
    for count_col, density_col in metric_mapping.items():
        if count_col in survey_results_df.columns:
            survey_results_df[density_col] = survey_results_df[count_col]

    # Get density columns for summarization
    density_columns = list(metric_mapping.values())
    value_cols = [c for c in density_columns if c in survey_results_df.columns]

    seasonal_summary_df = summarize_with_ci(
        survey_results_df,
        group_cols=["Period", "Site"],
        value_cols=value_cols,
    )

    # Calculate species richness
    # NOTE: this has to be aggregated per Site over the entire Period so it can't
    # be put through the same summarize_with_ci function as the other metrics
    species_richness_df = calculate_species_richness(survey_df)

    # Merge species richness with the summarized metrics
    seasonal_summary_df = seasonal_summary_df.merge(
        species_richness_df, on=["Period", "Site"], how="left"
    )

    return seasonal_summary_df
