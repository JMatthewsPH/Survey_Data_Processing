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
    validate_species_in_trophic_groups,
)
from utils import add_periods, create_daily_df, summarize_with_ci


def calculate_fish_metrics(
    pre_processed_fish_data_df: pd.DataFrame,
    daily_dive_numbers_df: pd.DataFrame,
    period: str,
) -> pd.DataFrame:
    """
    Calculate fish metrics for each Survey_ID before summarizing by season.
    """
    daily_fish_data_df = create_daily_df(pre_processed_fish_data_df, "fish")
    daily_fish_data_df = add_periods(daily_fish_data_df, period)

    # Validate that all species are in at least one trophic group
    validate_species_in_trophic_groups(daily_fish_data_df, "fish")

    daily_fish_data_df = calculate_biomass(
        daily_fish_data_df, "data/constants/biomass_coeffs_fish.csv"
    )

    base_daily = daily_fish_data_df[
        ["Survey_ID", "Date", "Period", "Site"]
    ].drop_duplicates()

    metric_frames = [
        calculate_total_count_and_density(daily_fish_data_df, daily_dive_numbers_df),
        calculate_commercial_count_and_density(
            daily_fish_data_df, daily_dive_numbers_df
        ),
        calculate_total_biomass_and_density(daily_fish_data_df, daily_dive_numbers_df),
        calculate_commercial_biomass(daily_fish_data_df, daily_dive_numbers_df),
        calculate_herbivore_density(daily_fish_data_df, daily_dive_numbers_df, "fish"),
        calculate_carnivore_density(daily_fish_data_df, daily_dive_numbers_df, "fish"),
        calculate_omnivore_density(daily_fish_data_df, daily_dive_numbers_df, "fish"),
        calculate_detritivore_density(
            daily_fish_data_df, daily_dive_numbers_df, "fish"
        ),
        calculate_corallivore_density(
            daily_fish_data_df, daily_dive_numbers_df, "fish"
        ),
    ]

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
        "Commercial Density",
        "Total Biomass Density",
        "Commercial Biomass Density",
    ]

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


def calculate_commercial_count_and_density(
    daily_fish_data_df: pd.DataFrame, dives_df: pd.Series
) -> pd.DataFrame:
    """
    Calculate daily commercial fish densities before seasonal summarization.
    """
    commercial_fish_names = (
        pd.read_csv("data/constants/commercial_fish.csv", header=None)
        .squeeze()
        .tolist()
    )
    commercial_count = (
        daily_fish_data_df[daily_fish_data_df["Species"].isin(commercial_fish_names)]
        .groupby(["Survey_ID", "Date", "Period", "Site"])["Total"]
        .sum()
        .reset_index()
        .rename(columns={"Total": "Commercial Count"})
    )

    commercial_count["Commercial Density"] = commercial_count.apply(
        lambda row: row["Commercial Count"] / dives_df.loc[row["Survey_ID"]],
        axis=1,
    )
    return commercial_count[
        ["Survey_ID", "Date", "Period", "Site", "Commercial Density"]
    ]


def calculate_commercial_biomass(
    daily_fish_data_df: pd.DataFrame, dives_df: pd.Series
) -> pd.DataFrame:
    """
    Calculate daily commercial biomass densities before seasonal summarization.
    """
    commercial_fish_names = (
        pd.read_csv("data/constants/commercial_fish.csv", header=None)
        .squeeze()
        .tolist()
    )
    commercial_biomass = (
        daily_fish_data_df[daily_fish_data_df["Species"].isin(commercial_fish_names)]
        .groupby(["Survey_ID", "Date", "Period", "Site"])["Total Biomass"]
        .sum()
        .reset_index()
        .rename(columns={"Total Biomass": "Commercial Biomass"})
    )

    commercial_biomass["Commercial Biomass"] = (
        commercial_biomass["Commercial Biomass"] / 1000
    )  # Convert to kg

    commercial_biomass["Commercial Biomass Density"] = commercial_biomass.apply(
        lambda row: row["Commercial Biomass"] / dives_df.loc[row["Survey_ID"]],
        axis=1,
    )

    return commercial_biomass[
        ["Survey_ID", "Date", "Period", "Site", "Commercial Biomass Density"]
    ]
