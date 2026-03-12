import pandas as pd
from fish_and_inverts_shared_metrics import (
    calculate_biomass,
    calculate_carnivore_density,
    calculate_corallivore_density,
    calculate_detritivore_density,
    calculate_herbivore_density,
    calculate_omnivore_density,
    calculate_total_biomass_and_density,
    calculate_total_count_and_density,
)
from utils import add_periods, create_daily_df, summarize_with_ci


def calculate_inverts_metrics(
    pre_processed_inverts_data_df: pd.DataFrame,
    daily_dive_numbers_df: pd.DataFrame,
    period: str,
    include_biomass: bool,
) -> pd.DataFrame:
    """
    Calculate invert metrics for each Date/Period/Site before summarizing by season.
    """
    daily_inverts_data_df = create_daily_df(pre_processed_inverts_data_df, "inverts")
    if include_biomass:
        daily_inverts_data_df = calculate_biomass(
            daily_inverts_data_df, "data/constants/biomass_coeffs_inverts.csv"
        )
    daily_inverts_data_df = add_periods(daily_inverts_data_df, period)

    base_daily = daily_inverts_data_df[
        ["Survey_ID", "Date", "Period", "Site"]
    ].drop_duplicates()

    metric_frames = [
        calculate_total_count_and_density(daily_inverts_data_df, daily_dive_numbers_df),
        calculate_herbivore_density(
            daily_inverts_data_df, daily_dive_numbers_df, "inverts"
        ),
        calculate_carnivore_density(
            daily_inverts_data_df, daily_dive_numbers_df, "inverts"
        ),
        calculate_omnivore_density(
            daily_inverts_data_df, daily_dive_numbers_df, "inverts"
        ),
        calculate_detritivore_density(
            daily_inverts_data_df, daily_dive_numbers_df, "inverts"
        ),
        calculate_corallivore_density(
            daily_inverts_data_df, daily_dive_numbers_df, "inverts"
        ),
    ]

    if include_biomass:
        metric_frames.append(
            calculate_total_biomass_and_density(
                daily_inverts_data_df, daily_dive_numbers_df
            )
        )

    daily_results_df = base_daily.copy()
    for frame in metric_frames:
        daily_results_df = daily_results_df.merge(
            frame, on=["Survey_ID", "Date", "Period", "Site"], how="left"
        )

    density_columns = [
        "Corallivore Density",
        "Detritivore Density",
        "Omnivore Density",
        "Carnivore Density",
        "Herbivore Density",
        "Total Density",
    ]
    if include_biomass:
        density_columns.append("Total Biomass Density")

    for column in density_columns:
        if column in daily_results_df.columns:
            daily_results_df[column] = daily_results_df[column].fillna(0)

    value_cols = [c for c in density_columns if c in daily_results_df.columns]

    seasonal_summary_df = summarize_with_ci(
        daily_results_df,
        group_cols=["Period", "Site"],
        value_cols=value_cols,
    )

    return seasonal_summary_df
