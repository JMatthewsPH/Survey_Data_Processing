import pandas as pd
from fish_pre_processing import pre_process_data, check_all_constants_exist
from utils import (
    determine_number_of_dives_per_period,
    save_site_dataframes,
)
from fish_metrics import (
    calculate_fish_metrics,
)

period = "seasonal" # seasonal or monthly

# Read in the all fish survey data from last season
all_fish_survey_data_df = pd.read_csv(
    "data/input/fish_survey_data_dec2024_feb2025.csv"
)
# all_invert_survey_data_df = pd.read_csv(
#     "data/input/inverts_survey_data_dec2024_feb2025.csv"
# )
# all_subs_survey_data_df = pd.read_csv(
#     "data/input/DBMCP_Substrates_2017-08-01_2025-05-29.csv"
# )

# Pre-process the fish data to prepare data for metric calculations
pre_processed_fish_df = pre_process_data(all_fish_survey_data_df)
# pre_processed_inverts_df = pre_process_data(all_invert_survey_data_df)

# # Check that all constants used in the fish metrics calculations exist
# check_all_constants_exist(pre_processed_fish_df)
# check_all_constants_exist(pre_processed_inverts_df)

# # Add fish and inverts data together
# fish_and_inverts_df = pd.concat(
#     [pre_processed_fish_df, pre_processed_inverts_df], ignore_index=True
# )

# Calculate the number of dives per day for each site
daily_dive_numbers_df = determine_number_of_dives_per_period(pre_processed_fish_df, period)


# Calculate metrics
fish_results_df = calculate_fish_metrics(
    pre_processed_fish_df, daily_dive_numbers_df, period
)


# Save metrics in total and per site
save_site_dataframes(fish_results_df, period, False)

# # Calculate unmatched fish species
# biomass_coeffs = pd.read_csv("data/constants/biomass_coeffs.csv", index_col="Species")
# unique_df_species = fish_daily_site_data_df["Species"].unique()
