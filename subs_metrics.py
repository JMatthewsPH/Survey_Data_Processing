import pandas as pd
from utils import prepare_results_df, add_periods, create_daily_df

def calculate_subs_metrics(pre_processed_subs_data_df: pd.DataFrame, daily_dive_numbers_df: pd.DataFrame,
    period: str) -> pd.DataFrame:
    """
    Calculate various subs metrics for each unique combination of Period and Site, or aggregated by month or season.

    Parameters:
    pre_processed_subs_data_df (pd.DataFrame): The DataFrame containing subs data.
    daily_dive_numbers_df (pd.DataFrame): The DataFrame containing the number of dives per day for each site.
    period (str): The period for aggregation. Options are "monthly", or "seasonal".

    Returns:
    pd.DataFrame: A DataFrame with aggregated metrics based on the specified period.
    """
    daily_subs_data_df = create_daily_df(pre_processed_subs_data_df, "subs")
    daily_subs_data_df = add_periods(daily_subs_data_df, period)

    results_df = prepare_results_df(daily_subs_data_df)
    results_df = calculate_hard_coral_cover(daily_subs_data_df, results_df, daily_dive_numbers_df)
    results_df = calculate_soft_coral_cover(daily_subs_data_df, results_df, daily_dive_numbers_df)
    results_df = calculate_fresh_algae_cover(daily_subs_data_df, results_df, daily_dive_numbers_df) 
    results_df = calculate_rubber_cover(daily_subs_data_df, results_df, daily_dive_numbers_df)
    results_df = calculate_bleaching(daily_subs_data_df, results_df, daily_dive_numbers_df)

    return results_df

def calculate_hard_coral_cover(daily_subs_data_df, results_df, daily_dive_numbers_df):
    """
    Calculate hard coral cover metrics.

    Parameters:
    daily_subs_data_df (pd.DataFrame): The DataFrame containing subs data.
    results_df (pd.DataFrame): The DataFrame to store results.
    daily_dive_numbers_df (pd.DataFrame): The DataFrame containing the number of dives per day for each site.

    Returns:
    pd.DataFrame: Updated results DataFrame with hard coral cover metrics.
    """
    # Count number of hard coral records
    hard_coral_cover = (
        daily_subs_data_df[daily_subs_data_df["Group"].str.contains("Hard Coral")]
        .groupby(["Period", "Site"])["Total"]
        .sum()
        .reset_index()
        .rename(columns={"Total": "Hard Coral Cover"})
    )

    # Normalise by the number of dives
    hard_coral_cover["Hard Coral Cover"] = hard_coral_cover.apply(
        lambda row: row["Hard Coral Cover"]
        / daily_dive_numbers_df.loc[(row["Period"], row["Site"])],
        axis=1,
    )
    return pd.merge(hard_coral_cover, results_df, "right").fillna(0)

def calculate_soft_coral_cover(daily_subs_data_df, results_df, daily_dive_numbers_df):
    """
    Calculate soft coral cover metrics.

    Parameters:
    daily_subs_data_df (pd.DataFrame): The DataFrame containing subs data.
    results_df (pd.DataFrame): The DataFrame to store results.
    daily_dive_numbers_df (pd.DataFrame): The DataFrame containing the number of dives per day for each site.

    Returns:
    pd.DataFrame: Updated results DataFrame with hard coral cover metrics.
    """
    # Count number of soft coral records
    soft_coral_cover = (
        daily_subs_data_df[daily_subs_data_df["Group"].str.contains("Soft Coral")]
        .groupby(["Period", "Site"])["Total"]
        .sum()
        .reset_index()
        .rename(columns={"Total": "Soft Coral Cover"})
    )

    # Normalise by the number of dives
    soft_coral_cover["Soft Coral Cover"] = soft_coral_cover.apply(
        lambda row: row["Soft Coral Cover"]
        / daily_dive_numbers_df.loc[(row["Period"], row["Site"])],
        axis=1,
    )
    return pd.merge(soft_coral_cover, results_df, "right").fillna(0)

def calculate_fresh_algae_cover(daily_subs_data_df, results_df, daily_dive_numbers_df):
    """
    Calculate fresh algae cover metrics.

    Parameters:
    daily_subs_data_df (pd.DataFrame): The DataFrame containing subs data.
    results_df (pd.DataFrame): The DataFrame to store results.
    daily_dive_numbers_df (pd.DataFrame): The DataFrame containing the number of dives per day for each site.

    Returns:
    pd.DataFrame: Updated results DataFrame with fresh algae cover metrics.
    """
    ## Count number of fresh algae records
    # Define fresh algae categories - I don't expect this to change hence why I've
    # defined it in code and not as an input file
    fresh_algae_categories = ["Algae Turf", "Algae Macro", "Algae Filamentous", "Algae Seagrass"]
    fresh_algae_cover = (
        daily_subs_data_df[daily_subs_data_df["Group"].isin(fresh_algae_categories)]
        .groupby(["Period", "Site"])["Total"]
        .sum()
        .reset_index()
        .rename(columns={"Total": "Fresh Algae Cover"})
    )

    # Normalise by the number of dives
    fresh_algae_cover["Fresh Algae Cover"] = fresh_algae_cover.apply(
        lambda row: row["Fresh Algae Cover"]
        / daily_dive_numbers_df.loc[(row["Period"], row["Site"])],
        axis=1,
    )
    return pd.merge(fresh_algae_cover, results_df, "right").fillna(0)

def calculate_rubber_cover(daily_subs_data_df, results_df, daily_dive_numbers_df): 
    """
    Calculate rubber cover metrics.

    Parameters:
    daily_subs_data_df (pd.DataFrame): The DataFrame containing subs data.
    results_df (pd.DataFrame): The DataFrame to store results.
    daily_dive_numbers_df (pd.DataFrame): The DataFrame containing the number of dives per day for each site.

    Returns:
    pd.DataFrame: Updated results DataFrame with rubber cover metrics.
    """
    # Count rubble records
    rubble_cover = (
        daily_subs_data_df[daily_subs_data_df["Group"].str.contains("Rubble")]
        .groupby(["Period", "Site"])["Total"]
        .sum()
        .reset_index()
        .rename(columns={"Total": "Rubble Cover"})
    )

    # Normalise by the number of dives
    rubble_cover["Rubble Cover"] = rubble_cover.apply(
        lambda row: row["Rubble Cover"]
        / daily_dive_numbers_df.loc[(row["Period"], row["Site"])],
        axis=1,
    )
    return pd.merge(rubble_cover, results_df, "right").fillna(0)

def calculate_bleaching(daily_subs_data_df, results_df, daily_dive_numbers_df):
    """
    Calculate bleaching metrics - Fully Bleached counts as 1, Partially Bleached counts as 0.5.

    Parameters:
    daily_subs_data_df (pd.DataFrame): The DataFrame containing subs data.
    results_df (pd.DataFrame): The DataFrame to store results.
    daily_dive_numbers_df (pd.DataFrame): The DataFrame containing the number of dives per day for each site.

    Returns:
    pd.DataFrame: Updated results DataFrame with bleaching metrics.
    """
    # Count fully bleached records
    fully_bleached_cover = (
        daily_subs_data_df[daily_subs_data_df["Status"] == "Fully Bleaching"]
        .groupby(["Period", "Site"])["Total"]
        .sum()
        .reset_index()
        .rename(columns={"Total": "Fully Bleached"})
    )   
    results_df = pd.merge(results_df, fully_bleached_cover, how="left").fillna(0)
    # Count partially bleached records and divide by 2
    partially_bleached_cover = (
        daily_subs_data_df[daily_subs_data_df["Status"] == "Partially Bleaching"]
        .groupby(["Period", "Site"])["Total"]
        .sum()
        .reset_index()
        .rename(columns={"Total": "Partially Bleached"})
    )
    results_df = pd.merge(results_df, partially_bleached_cover, how="left").fillna(0)

    results_df["Bleaching"] = results_df.apply(
        lambda row: (row["Fully Bleached"] + row["Partially Bleached"]/2)
        / daily_dive_numbers_df.loc[(row["Period"], row["Site"])],
        axis=1,
    )
    results_df.drop(["Fully Bleached", "Partially Bleached"], axis=1, inplace=True)
    return results_df