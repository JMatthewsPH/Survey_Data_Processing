import pandas as pd
from utils import prepare_results_df, add_periods, create_daily_df
from fish_and_inverts_shared_metrics import (
    calculate_total_count_and_density,
    calculate_commercial_count_and_density,
    calculate_biomass_metrics,  
    calculate_herbivore_density,
    calculate_carnivore_density,
    calculate_omnivore_density,
    calculate_detritivore_density,
    calculate_corallivore_density,
    calculate_biomass
)


def calculate_fish_metrics(
    pre_processed_fish_data_df: pd.DataFrame,
    daily_dive_numbers_df: pd.DataFrame,
    period: str,
) -> pd.DataFrame:
    """
    Calculate various fish metrics for each unique combination of Period and Site, or aggregated by month or season.

    Parameters:
    daily_fish_data_df (pd.DataFrame): The DataFrame containing fish data.
    daily_dive_numbers_df (pd.DataFrame): The DataFrame containing the number of dives per day for each site.
    period (str): The period for aggregation. Options are "daily", "monthly", or "seasonal".

    Returns:
    pd.DataFrame: A DataFrame with aggregated metrics based on the specified period.
    """
    daily_fish_data_df = create_daily_df(pre_processed_fish_data_df)
    daily_fish_data_df = calculate_biomass(daily_fish_data_df, "data/constants/biomass_coeffs_fish.csv")
    daily_fish_data_df = add_periods(daily_fish_data_df, period)

    results_df = prepare_results_df(daily_fish_data_df)
    results_df = calculate_total_count_and_density(
        daily_fish_data_df, results_df, daily_dive_numbers_df
    )
    results_df = calculate_commercial_count_and_density(
        daily_fish_data_df, results_df, daily_dive_numbers_df
    )
    results_df = calculate_biomass_metrics(daily_fish_data_df, results_df, daily_dive_numbers_df)
    results_df = calculate_herbivore_density(
        daily_fish_data_df, results_df, daily_dive_numbers_df, "fish"
    )
    results_df = calculate_carnivore_density(
        daily_fish_data_df, results_df, daily_dive_numbers_df, "fish"
    )
    results_df = calculate_omnivore_density(
        daily_fish_data_df, results_df, daily_dive_numbers_df, "fish"
    )
    results_df = calculate_detritivore_density(
        daily_fish_data_df, results_df, daily_dive_numbers_df, "fish"
    )
    results_df = calculate_corallivore_density(
        daily_fish_data_df, results_df, daily_dive_numbers_df, "fish"
    )

    return results_df.groupby(["Period", "Site"]).sum().reset_index()
    
