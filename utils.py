import pandas as pd


def determine_number_of_dives_per_day(
    survey_data_df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Determine the number of dives per day for each site.

    Parameters:
    survey_data_df (pd.DataFrame): The DataFrame containing all fish data.

    Returns:
    pd.DataFrame: The DataFrame with the number of dives per day for each site.
    """
    return survey_data_df.groupby(["Date", "Site"])["Survey_ID"].nunique()


def prepare_results_df(survey_data_df: pd.DataFrame) -> pd.DataFrame:
    """
    Extract a DataFrame with one row for each unique combination of Date and Site.

    Parameters:
    survey_data_df (pd.DataFrame): The DataFrame containing all fish data.

    Returns:
    pd.DataFrame: A DataFrame with unique combinations of Date and Site.
    """
    unique_combinations = (
        survey_data_df[["Period", "Site"]].drop_duplicates().reset_index(drop=True)
    )
    return unique_combinations


# Create separate DataFrames for each site and save them as CSV files
def save_site_dataframes(daily_fish_results_df: pd.DataFrame, period: str):
    """
    Create separate DataFrames for each site and save them as CSV files.

    Parameters:
    daily_fish_results_df (pd.DataFrame): The DataFrame containing daily fish results.
    """
    output_dir = "data/output/"
    for site, site_df in daily_fish_results_df.groupby("Site"):
        site_filename = f"{output_dir}/{period}/daily_fish_results_{site}.csv"
        site_df.to_csv(site_filename, index=False)
        print(f"Saved {site_filename}")
