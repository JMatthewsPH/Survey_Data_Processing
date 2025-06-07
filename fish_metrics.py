import pandas as pd
from utils import prepare_results_df, add_periods, create_daily_df
from fish_and_inverts_shared_metrics import (
    calculate_total_count_and_density,
    calculate_biomass,  
    calculate_total_biomass_and_density,
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
    daily_fish_data_df = create_daily_df(pre_processed_fish_data_df, "fish")
    daily_fish_data_df = calculate_biomass(daily_fish_data_df, "data/constants/biomass_coeffs_fish.csv")
    daily_fish_data_df = add_periods(daily_fish_data_df, period)

    results_df = prepare_results_df(daily_fish_data_df)
    results_df = calculate_total_count_and_density(
        daily_fish_data_df, results_df, daily_dive_numbers_df
    )
    results_df = calculate_commercial_count_and_density(
        daily_fish_data_df, results_df, daily_dive_numbers_df
    )
    results_df = calculate_total_biomass_and_density(daily_fish_data_df, results_df, daily_dive_numbers_df)
    results_df = calculate_commercial_biomass(daily_fish_data_df, results_df, daily_dive_numbers_df)
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


def calculate_commercial_count_and_density(daily_fish_data_df: pd.DataFrame, results_df: pd.DataFrame, dives_df: pd.DataFrame
) -> pd.DataFrame:
    """
    Calculate the total fish count and total density for each unique combination of Period and Site.

    Parameters:
    daily_fish_data_df (pd.DataFrame): The DataFrame containing fish data.
    results_df (pd.DataFrame): The DataFrame containing the number of dives per day for each site.

    Returns:
    pd.DataFrame: A DataFrame with Period, Site, Total Fish Count, and Total Density.
    """
    # Read in commercial fish names
    commercial_fish_names = (
        pd.read_csv("data/constants/commercial_fish.csv", header=None)
        .squeeze()
        .tolist()
    )
    # Count total fish per site per day that are commercial
    commercial_count = (
        daily_fish_data_df[daily_fish_data_df["Species"].isin(commercial_fish_names)]
        .groupby(["Period", "Site"])["Total"]
        .sum()
        .reset_index()
        .rename(columns={"Total": "Commercial Count"})
    )

    # Calculate commercial density by dividing total fish count by the number of dives
    commercial_count["Commercial Density"] = commercial_count.apply(
        lambda row: row["Commercial Count"] / dives_df.loc[(row["Period"], row["Site"])],
        axis=1,
    )
    results_df["Commercial Density"] = commercial_count["Commercial Density"]
    return results_df

def calculate_commercial_biomass(
    daily_fish_data_df: pd.DataFrame, results_df: pd.DataFrame, dives_df: pd.DataFrame
) -> pd.DataFrame:
    """
    Calculate the total commercial biomass for each unique combination of Period and Site.

    Parameters:
    daily_fish_data_df (pd.DataFrame): The DataFrame containing fish data.
    commercial_fish_names (list): A list of species names considered commercial.

    Returns:
    pd.DataFrame: A DataFrame with Period, Site, and the summed commercial biomass.
    """
    commercial_fish_names = (
        pd.read_csv("data/constants/commercial_fish.csv", header=None)
        .squeeze()
        .tolist()
    )
    # Calculate commercial biomass per site per day
    commercial_biomass = (
        daily_fish_data_df[daily_fish_data_df["Species"].isin(commercial_fish_names)]
        .groupby(["Period", "Site"])["Total Biomass"]
        .sum()
        .reset_index()
        .rename(columns={"Total Biomass": "Commercial Biomass"})
    )

    commercial_biomass["Commercial Biomass"] = commercial_biomass["Commercial Biomass"] / 1000  # Convert to kg

    # Calculate commercial density by dividing total fish count by the number of dives
    commercial_biomass["Commercial Biomass Density"] = commercial_biomass.apply(
        lambda row: row["Commercial Biomass"] / dives_df.loc[(row["Period"], row["Site"])],
        axis=1,
    )
    
    results_df["Commercial Biomass Density"] = commercial_biomass["Commercial Biomass Density"]
    return results_df

    
