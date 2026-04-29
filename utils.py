import glob
import os
import re
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats


def determine_number_of_surveys_per_site_for_period(
    survey_data_df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Determine the number of surveys per site for each period.

    Parameters:
    survey_data_df (pd.DataFrame): The DataFrame containing all survey data.

    Returns:
    pd.DataFrame: The DataFrame with the number of surveys per site for each period.
    """
    surveys_per_site_per_period_df = (
        survey_data_df.groupby(["Period", "Site"])["Survey_ID"]
        .nunique()
        .reset_index(name="Number of Surveys")
    )
    return surveys_per_site_per_period_df


def add_periods(time_df: pd.DataFrame, period: str) -> pd.DataFrame:
    """
    Determine the period for each survey based on the date.

    Parameters:
    time_df (pd.DataFrame): Any dataframe containing a 'Date' column (will be used for
    fish survey data and dive data.
    period (str): The period type for aggregation:
        - "monthly": Groups by month
        - "seasonal": Groups by individual seasons (Spring, Summer, Autumn, Winter)
        - "biannual": Groups by 6-month periods (Spring/Summer: Mar-Aug, Autumn/Winter: Sep-Feb)

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
                season = f"Winter {str(year)[-2:]}/{str(year + 1)[-2:]}"
            else:
                season = f"Winter {str(year - 1)[-2:]}/{str(year)[-2:]}"
        elif month in [3, 4, 5]:
            season = f"Spring {year}"
        elif month in [6, 7, 8]:
            season = f"Summer {year}"
        else:
            season = f"Autumn {year}"
        return season

    def map_date_to_biannual(date: pd.Timestamp) -> str:
        """
        Map a date to a 6-month period label.
        Sep-Feb: 'Autumn/Winter 24/25'
        Mar-Aug: 'Spring/Summer 24'

        Parameters:
        date (pd.Timestamp): The date to map.

        Returns:
        str: The biannual period label.
        """
        month = date.month
        year = date.year

        if month in [3, 4, 5, 6, 7, 8]:
            # Spring/Summer: Mar-Aug
            period = f"Spring/Summer {str(year)[-2:]}"
        else:
            # Autumn/Winter: Sep-Feb (spans two years)
            if month in [9, 10, 11, 12]:
                # Sep-Dec: Start of Autumn/Winter period
                period = f"Autumn/Winter {str(year)[-2:]}/{str(year + 1)[-2:]}"
            else:  # month in [1, 2]
                # Jan-Feb: End of Autumn/Winter period
                period = f"Autumn/Winter {str(year - 1)[-2:]}/{str(year)[-2:]}"
        return period

    if period == "monthly":
        time_df["Period"] = time_df["Date"].dt.to_period("M")
    elif period == "seasonal":
        time_df["Period"] = time_df["Date"].map(map_date_to_season)
    elif period == "biannual":
        time_df["Period"] = time_df["Date"].map(map_date_to_biannual)
    return time_df


def prepare_survey_df(
    all_survey_data_df: pd.DataFrame, group: str, period: str
) -> pd.DataFrame:
    """
    Prepares dataframe for use in metric calculation - adding and
    removing rows.

    all_survey_data_df (pd.DataFrame): The DataFrame containing all data
    at individual survey level.
    group (str): The data group (e.g., "fish", "inverts", "subs").
    period (str): The period for aggregation (e.g., "seasonal", "monthly", "biannual").

    Returns:
    pd.DataFrame: A DataFrame with one row per unique survey (Survey_ID) and
    either Species and Size for fish/inverts or Group and Status for substrates,
    displaying the aggregated totals along with a Total column. Keeps Depth for
    depth-specific richness calculations.
    """
    # Add period information
    prepared_df = add_periods(all_survey_data_df, period)
    # Remove unused columns (keeping Depth for species richness calculations)
    prepared_df = prepared_df.drop(
        columns=["Zone", "Water_Temp", "Visibility", "Current"]
    )
    return prepared_df


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


def save_all_sites_dataframes(
    results_df: pd.DataFrame, period: str, group: str
) -> None:
    """
    Prepare resutls dataframe and save to CSV

    Parameters:
    results_df (pd.DataFrame): The DataFrame containing daily fish results.
    period (str): The period for aggregation (e.g., "seasonal", "monthly", "biannual").
    group (str): The data group (e.g., "fish", "inverts", "subs").
    """
    # Define sites to exclude from output
    excluded_sites = {
        "BONBONON",
        "DAUIN POBLACION MPA",
        "MASAPLOD NORTE MPA",
        "TAMBOBO MPA",
        "TURTLE HEAVEN",
        "UNITY POINT",
        "WELLBEACH",
    }
    # Drop rows with site in excluded_sites
    results_df = results_df[~results_df["Site"].isin(excluded_sites)]
    # Order columns by season and year
    results_df["sort_key"] = results_df["Period"].apply(period_sort_key)
    results_df = results_df.sort_values("sort_key").drop(columns="sort_key")

    # Round all values for 2 decimal places
    results_df = results_df.round(2)

    output_dir = "data/output"
    if not os.path.exists(f"{output_dir}/{group}/{period}"):
        os.makedirs(f"{output_dir}/{group}/{period}")

    # Filter out excluded sites and save only the ones we want
    filename = f"{output_dir}/{group}/{period}/All Sites.csv"
    results_df.to_csv(filename, index=False)
    print(f"Saved {filename}")


# Create separate DataFrames for each site and save them as CSV files
def save_individual_site_dataframes(
    results_df: pd.DataFrame, period: str, group: str
) -> None:
    """
    Create separate DataFrames for each site and save them as CSV files.

    Parameters:
    results_df (pd.DataFrame): The DataFrame containing daily fish results.
    period (str): The period for aggregation (e.g., "seasonal", "monthly", "biannual").
    group (str): The data group (e.g., "fish", "inverts", "subs").
    """
    # Define sites to exclude from output
    excluded_sites = {
        "BONBONON",
        "DAUIN POBLACION MPA",
        "MASAPLOD NORTE MPA",
        "TAMBOBO MPA",
        "TURTLE HEAVEN",
        "UNITY POINT",
        "WELLBEACH",
    }
    # Order columns by season and year
    results_df["sort_key"] = results_df["Period"].apply(period_sort_key)
    results_df = results_df.sort_values("sort_key").drop(columns="sort_key")

    # Round all values for 2 decimal places
    results_df = results_df.round(2)

    output_dir = "data/output"
    if not os.path.exists(f"{output_dir}/{group}/{period}"):
        os.makedirs(f"{output_dir}/{group}/{period}")

    # Filter out excluded sites and save only the ones we want
    for site, site_df in results_df.groupby("Site"):
        if site not in excluded_sites:
            site_filename = f"{output_dir}/{group}/{period}/{site}.csv"
            site_df.to_csv(site_filename, index=False)
            print(f"Saved {site_filename}")
        else:
            print(f"Skipped {site} (excluded from output)")


def period_sort_key(period_str):
    """
    Sort key function for period strings.
    Handles seasonal (e.g., "Winter 17/18", "Autumn 2018"),
    biannual (e.g., "Spring/Summer 24", "Autumn/Winter 24/25"),
    and monthly periods.
    """
    # Try to match biannual format first (e.g., "Spring/Summer 24" or "Autumn/Winter 24/25")
    biannual_match = re.match(r"(\w+)/(\w+)\s+(\d{2,4})(?:/(\d{2}))?", period_str)
    if biannual_match:
        season1, season2, year1, year2 = biannual_match.groups()
        # Convert to full year
        year1 = int(year1) if len(year1) == 4 else 2000 + int(year1)
        if year2:
            year2 = 2000 + int(year2)
            year = year1  # Use the first year for sorting
        else:
            year = year1

        # Assign order: Spring/Summer=0.5, Autumn/Winter=3.5
        if season1 == "Spring":
            s_order = 0.5  # Spring/Summer comes first
        else:
            s_order = 3.5  # Autumn/Winter comes after
        return (year, s_order)

    # Match seasonal format (e.g., "Winter 17/18", "Autumn 2018")
    seasonal_match = re.match(r"(\w+)\s+(\d{2,4})(?:/(\d{2}))?", period_str)
    if seasonal_match:
        season, year1, year2 = seasonal_match.groups()
        # Convert to full year
        year1 = int(year1) if len(year1) == 4 else 2000 + int(year1)
        if year2:
            year2 = 2000 + int(year2)
            year = year1  # Use the first year for sorting
        else:
            year = year1

        # Assign season order: Winter=4, Spring=1, Summer=2, Autumn=3
        season_order = {"Winter": 4, "Spring": 1, "Summer": 2, "Autumn": 3}
        s_order = season_order.get(season, 99)
        return (year, s_order)

    # If no match, put at end
    return (9999, 99)


def find_latest_data_files(input_dir: str = "data/input") -> dict:
    """
    Automatically find the latest data files in the input directory.

    Parameters:
    input_dir (str): Path to the input directory containing data files.

    Returns:
    dict: Dictionary with file types as keys and file paths as values.
    """
    input_path = Path(input_dir)

    # Define file patterns for each data type
    file_patterns = {
        "fish": ["DBMCP_Fish_*.csv", "fish_*.csv"],
        "inverts": ["DBMCP_Inverts_*.csv", "inverts_*.csv"],
        "predation": ["DBMCP_Predation_*.csv", "predation_*.csv"],
        "subs": ["DBMCP_Substrates_*.csv", "subs_*.csv", "substrates_*.csv"],
    }

    found_files = {}

    for data_type, patterns in file_patterns.items():
        latest_file = None
        latest_mtime = 0

        for pattern in patterns:
            # Search for files matching the pattern
            matching_files = list(input_path.glob(pattern))

            for file_path in matching_files:
                # Get file modification time
                mtime = file_path.stat().st_mtime

                # Keep track of the most recent file
                if mtime > latest_mtime:
                    latest_mtime = mtime
                    latest_file = file_path

        if latest_file:
            found_files[data_type] = str(latest_file)
            print(f"Found {data_type} data file: {latest_file.name}")
        else:
            print(
                f"Warning: No {data_type} data file found matching patterns: {patterns}"
            )

    return found_files
