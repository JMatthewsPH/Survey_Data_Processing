import pandas as pd
from fish_pre_processing import pre_process_fish_data
from utils import (
    determine_number_of_dives_per_day,
    save_site_dataframes,
)
from fish_metrics import (
    calculate_fish_metrics,
)

# Read in the all fish survey data from last season
all_fish_survey_data_df = pd.read_csv(
    "data/input/DBMCP_Fish_2017-08-01_2025-05-10_ALL.csv"
)
print(all_fish_survey_data_df.head())
print(len(all_fish_survey_data_df))

# Pre-process the fish data to prepare data for metric calculations
pre_processed_fish_df = pre_process_fish_data(all_fish_survey_data_df)
print(len(pre_processed_fish_df))
print(pre_processed_fish_df.head())

# Calculate the number of dives per day for each site
daily_dive_numbers_df = determine_number_of_dives_per_day(pre_processed_fish_df)
print(daily_dive_numbers_df.head(20))


# Calculate metrics
fish_results_df = calculate_fish_metrics(
    pre_processed_fish_df, daily_dive_numbers_df, "monthly"
)


# Save metrics in total and per site
fish_results_df.to_csv("data/last_season_fish_daily_site_data.csv", index=False)
save_site_dataframes(fish_results_df, "season")

# # Calculate unmatched fish species
# biomass_coeffs = pd.read_csv("data/constants/biomass_coeffs.csv", index_col="Species")
# unique_df_species = fish_daily_site_data_df["Species"].unique()
