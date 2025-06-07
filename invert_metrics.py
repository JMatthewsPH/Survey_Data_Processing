import pandas as pd
from utils import prepare_results_df, add_periods, create_daily_df
from fish_and_inverts_shared_metrics import (
    calculate_biomass,
    calculate_total_biomass_and_density,
    calculate_total_count_and_density, 
    calculate_herbivore_density,
    calculate_carnivore_density,
    calculate_omnivore_density,
    calculate_detritivore_density,
    calculate_corallivore_density
)

def calculate_inverts_metrics(
    pre_processed_inverts_data_df: pd.DataFrame,
    daily_dive_numbers_df: pd.DataFrame,
    period: str,
    include_biomass: bool
) -> pd.DataFrame:
    """
    Calculate various inverts metrics for each unique combination of Period and Site, or aggregated by month or season.

    Parameters:
    daily_inverts_data_df (pd.DataFrame): The DataFrame containing inverts data.
    daily_dive_numbers_df (pd.DataFrame): The DataFrame containing the number of dives per day for each site.
    period (str): The period for aggregation. Options are "daily", "monthly", or "seasonal".
    include_biomass (bool): True/False indicating whether or not to calculate biomass metrics
    NOTE: When implemented biomass coefficients for inverts were not yet available.

    Returns:
    pd.DataFrame: A DataFrame with aggregated metrics based on the specified period.
    """
    daily_inverts_data_df = create_daily_df(pre_processed_inverts_data_df, "inverts")
    # TODO: Remove this boolean when biomass coeficients for inverts become available
    if include_biomass:
        daily_inverts_data_df = calculate_biomass(daily_inverts_data_df, "data/constants/biomass_coeffs_inverts.csv")
    daily_inverts_data_df = add_periods(daily_inverts_data_df, period)

    results_df = prepare_results_df(daily_inverts_data_df)
    results_df = calculate_total_count_and_density(
        daily_inverts_data_df, results_df, daily_dive_numbers_df
    )
    # results_df = calculate_commercial_count_and_density(
    #     daily_inverts_data_df, results_df, daily_dive_numbers_df
    # )
    # TODO: Remove this boolean when biomass coeficients for inverts become available
    if include_biomass:
        results_df = calculate_total_biomass_and_density(daily_inverts_data_df, results_df, daily_dive_numbers_df)

    results_df = calculate_herbivore_density(
        daily_inverts_data_df, results_df, daily_dive_numbers_df, "inverts"
    )
    results_df = calculate_carnivore_density(
        daily_inverts_data_df, results_df, daily_dive_numbers_df, "inverts"
    )
    results_df = calculate_omnivore_density(
        daily_inverts_data_df, results_df, daily_dive_numbers_df, "inverts"
    )
    results_df = calculate_detritivore_density(
        daily_inverts_data_df, results_df, daily_dive_numbers_df, "inverts"
    )
    results_df = calculate_corallivore_density(
        daily_inverts_data_df, results_df, daily_dive_numbers_df, "inverts"
    )

    return results_df.groupby(["Period", "Site"]).sum().reset_index()
