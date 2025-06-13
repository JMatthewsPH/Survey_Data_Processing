import pandas as pd
import re
import os


def determine_number_of_dives_per_period(
    survey_data_by_day_df: pd.DataFrame, period: str
) -> pd.DataFrame:
    """
    Determine the number of dives per day for each site.

    Parameters:
    survey_data_df (pd.DataFrame): The DataFrame containing all fish data.

    Returns:
    pd.DataFrame: The DataFrame with the number of dives per day for each site.
    """
    survey_data_by_day_df = add_periods(survey_data_by_day_df, period)
    survey_data_by_day_df = survey_data_by_day_df.groupby(["Period", "Site"])["Survey_ID"].nunique()
    return survey_data_by_day_df

def add_periods(time_df: pd.DataFrame, period: str) -> pd.DataFrame:
    """
    Determine the period for each survey based on the date.

    Parameters:
    time_df (pd.DataFrame): Any dataframe containing a 'Date' column (will be used for 
    fish survey data and dive data.

    Returns:
    pd.DataFrame: The DataFrame with the period for each survey.
    """

    def map_date_to_season(date: pd.Timestamp) -> str:
        """
        Map a date to a season label, e.g., 'Spring 2016' or 'Winter 2017/2018'.

        Parameters:
        date (pd.Timestamp): The date to map.

        Returns:
        str: The season label.
        """
        month = date.month
        year = date.year

        if month in [12, 1, 2]:
            # Winter spans two years
            if month == 12:
                season = f"Winter {str(year)[-2:]}/{str(year+1)[-2:]}"
            else:
                season = f"Winter {str(year-1)[-2:]}/{str(year)[-2:]}"
        elif month in [3, 4, 5]:
            season = f"Spring {year}"
        elif month in [6, 7, 8]:
            season = f"Summer {year}"
        else:
            season = f"Autumn {year}"
        return season

    if period == "monthly":
        time_df["Period"] = time_df["Date"].dt.to_period("M")
    elif period == "seasonal":
        time_df["Period"] = time_df["Date"].map(map_date_to_season)
    return time_df

def create_daily_df(all_survey_data_df: pd.DataFrame, group: str) -> pd.DataFrame:
    """
    Aggregate all fish survey data to create a dataframe that shows the total biomass
    and number of fish spotted for each fish category of each size seen on each day at
    each dive site. This is used to calculate the fish metrics for any period.

    all_fish_survey_data_df (pd.DataFrame): The DataFrame containing all fish data
    at indivudual survey level.

    Returns:
    pd.DataFrame: A DataFrame containing the total biomass and number of fish spotted
    for each fish category of each size per day and dive site
    """
    if group != "subs":
        aggregated_df = (
            all_survey_data_df.groupby(["Date", "Site", "Species", "Size"])
            .agg({"Total": "sum"})
            .reset_index()
        )
    else:
        aggregated_df = (
            all_survey_data_df.groupby(["Date", "Site", "Group", "Status"])
            .agg({"Total": "sum"})
            .reset_index()
        )
    return aggregated_df

def prepare_results_df(survey_data_df: pd.DataFrame) -> pd.DataFrame:
    """
    Extract a DataFrame with one row for each unique combination of Period and Site.

    Parameters:
    survey_data_df (pd.DataFrame): The DataFrame containing all fish data.

    Returns:
    pd.DataFrame: A DataFrame with unique combinations of Period and Site.
    """
    unique_combinations = (
        survey_data_df[["Period", "Site"]].drop_duplicates().reset_index(drop=True)
    )
    return unique_combinations


# Create separate DataFrames for each site and save them as CSV files
def save_site_dataframes(daily_fish_results_df: pd.DataFrame, period: str, group: str) -> None:
    """
    Create separate DataFrames for each site and save them as CSV files.

    Parameters:
    daily_fish_results_df (pd.DataFrame): The DataFrame containing daily fish results.
    """
    # Order columns by season and year
    daily_fish_results_df["sort_key"] = daily_fish_results_df["Period"].apply(period_sort_key)
    daily_fish_results_df = daily_fish_results_df.sort_values("sort_key").drop(columns="sort_key")

    # Round all values for 2 decimal places
    daily_fish_results_df = daily_fish_results_df.round(2)

    output_dir = "data/output"
    if not os.path.exists(f"{output_dir}/{group}/{period}"):
        os.makedirs(f"{output_dir}/{group}/{period}")
    for site, site_df in daily_fish_results_df.groupby("Site"):
        site_filename = f"{output_dir}/{group}/{period}/{site}.csv"
        site_df.to_csv(site_filename, index=False)
        print(f"Saved {site_filename}")


def period_sort_key(period_str):
    # Match e.g. "Winter 17/18", "Autumn 2018", etc.
    match = re.match(r"(\w+)\s+(\d{2,4})(?:/(\d{2}))?", period_str)
    if not match:
        return (9999, 99)  # Put unrecognized at end

    season, year1, year2 = match.groups()
    # Convert to full year
    year1 = int(year1) if len(year1) == 4 else 2000 + int(year1)
    if year2:
        year2 = 2000 + int(year2)
        year = year1  # Use the first year for sorting
    else:
        year = year1

    # Assign season order: Winter=0, Spring=1, Summer=2, Autumn=3
    season_order = {"Winter": 4, "Spring": 1, "Summer": 2, "Autumn": 3}
    s_order = season_order.get(season, 99)
    return (year, s_order)
