import pandas as pd
import re
import os
import glob
from pathlib import Path

import numpy as np
from scipy import stats


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
    period (str): The period for aggregation (e.g., "seasonal", "monthly").
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
        "WELLBEACH"
    }
    # Order columns by season and year
    daily_fish_results_df["sort_key"] = daily_fish_results_df["Period"].apply(period_sort_key)
    daily_fish_results_df = daily_fish_results_df.sort_values("sort_key").drop(columns="sort_key")

    # Round all values for 2 decimal places
    daily_fish_results_df = daily_fish_results_df.round(2)

    output_dir = "data/output"
    if not os.path.exists(f"{output_dir}/{group}/{period}"):
        os.makedirs(f"{output_dir}/{group}/{period}")
    
    # Filter out excluded sites and save only the ones we want
    for site, site_df in daily_fish_results_df.groupby("Site"):
        if site not in excluded_sites:
            site_filename = f"{output_dir}/{group}/{period}/{site}.csv"
            site_df.to_csv(site_filename, index=False)
            print(f"Saved {site_filename}")
        else:
            print(f"Skipped {site} (excluded from output)")


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
        'fish': ['DBMCP_Fish_*.csv', 'fish_*.csv'],
        'inverts': ['DBMCP_Inverts_*.csv', 'inverts_*.csv'],
        'predation': ['DBMCP_Predation_*.csv', 'predation_*.csv'],
        'subs': ['DBMCP_Substrates_*.csv', 'subs_*.csv', 'substrates_*.csv']
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
            print(f"Warning: No {data_type} data file found matching patterns: {patterns}")
    
    return found_files


def summarize_with_ci(df, group_cols, value_cols, confidence=0.95):
    
    records = []
    grouped = df.groupby(group_cols)
    for keys, g in grouped:
        row = dict(zip(group_cols, keys if isinstance(keys, tuple) else (keys,)))
        for col in value_cols:
            data = pd.to_numeric(g[col], errors="coerce").dropna()
            n = data.size
            if n == 0:
                mean = sd = se = ci_low = ci_high = eb_low = eb_high = np.nan
            elif n == 1:
                mean = float(data.iloc[0])
                sd = se = ci_low = ci_high = eb_low = eb_high = np.nan
            else:
                mean = data.mean()
                sd = data.std(ddof=1)
                se = stats.sem(data, nan_policy="omit")
                tcrit = stats.t.ppf((1 + confidence) / 2.0, df=n - 1)
                margin = tcrit * se
                ci_low, ci_high = mean - margin, mean + margin
                eb_low, eb_high = mean - se, mean + se

            row[col] = mean
            row[f"{col}_N"] = int(n) if n == n else np.nan
            row[f"{col}_SD"] = sd
            row[f"{col}_SE"] = se
            row[f"{col}_CI_low"] = ci_low
            row[f"{col}_CI_high"] = ci_high
            row[f"{col}_EB_low"] = eb_low
            row[f"{col}_EB_high"] = eb_high
        records.append(row)

    out = pd.DataFrame.from_records(records)
    order = list(group_cols) + [c for c in out.columns if c not in group_cols]
    return out.loc[:, order]

    
