import pandas as pd
from pre_processing import pre_process_data, check_all_constants_exist
from utils import (
    determine_number_of_dives_per_period,
    save_site_dataframes,
)
from fish_metrics import (
    calculate_fish_metrics,
)

period = "seasonal" # seasonal or monthly

## Read in survey data 
all_fish_survey_data_df = pd.read_csv(
    "data/input/DBMCP_Fish_2024-12-01_2025-02-28.csv"
)
# all_invert_survey_data_df = pd.read_csv(
#     "data/input/inverts_survey_data_dec2024_feb2025.csv"
# )
# all_subs_survey_data_df = pd.read_csv(
#     "data/input/DBMCP_Substrates_2017-08-01_2025-05-29.csv"
# )

## Pre-process survey data
pre_processed_fish_df = pre_process_data(all_fish_survey_data_df)
# pre_processed_inverts_df = pre_process_data(all_invert_survey_data_df)

# # Check that all constants used in the fish metrics calculations exist
# fish_and_inverts_df = pd.concat(
#     [pre_processed_fish_df, pre_processed_inverts_df], ignore_index=True
# )
check_all_constants_exist(pre_processed_fish_df)

## Calculate metrics
# First, calculate the number of dives per day for each site
daily_dive_numbers_df = determine_number_of_dives_per_period(pre_processed_fish_df, period)
# Calculate metrics
fish_results_df = calculate_fish_metrics(
    pre_processed_fish_df, daily_dive_numbers_df, period
)

## Save results to CSV
save_site_dataframes(fish_results_df, period, False)

