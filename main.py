import pandas as pd
from pre_processing import pre_process_data, check_all_constants_exist_for_fish, check_all_constants_exist_for_inverts
from subs_metrics import calculate_subs_metrics
from utils import (
    determine_number_of_dives_per_period,
    save_site_dataframes,
)
from fish_metrics import (
    calculate_fish_metrics,
)
from invert_metrics import (
    calculate_inverts_metrics,
)

period = "seasonal" # seasonal or monthly

### FISH

## Read in survey data 
all_fish_survey_data_df = pd.read_csv(
    "data/input/DBMCP_Fish_2017-08-01_2025-05-31.csv"
)

## Pre-process survey data
pre_processed_fish_df = pre_process_data(all_fish_survey_data_df, group="fish")
# Check that all constants used in the fish metrics calculations exist
check_all_constants_exist_for_fish(pre_processed_fish_df)

## Calculate metrics
# First, calculate the number of dives per day for each site
fish_daily_dive_numbers_df = determine_number_of_dives_per_period(pre_processed_fish_df, period)
# Calculate metrics
fish_results_df = calculate_fish_metrics(
    pre_processed_fish_df, fish_daily_dive_numbers_df, period
)
## Save results to CSV
save_site_dataframes(fish_results_df, period, group="fish")

#-------------------------------------------------------------------------------------------
### INVERTS
## WHEN BIOMASS COEFFICIENTS BECOME AVAILABLE FOR INVERTS, YOU NEED TO CHANGE TWO THINGS BELOW
## Read in survey data 
all_invert_survey_data_df = pd.read_csv(
    "data/input/DBMCP_Inverts_2017-08-01_2025-05-31.csv"
)
## Pre-process survey data
pre_processed_inverts_df = pre_process_data(all_invert_survey_data_df, group="inverts")
# Check that all constants used in the fish metrics calculations exist
check_all_constants_exist_for_inverts(pre_processed_inverts_df, include_biomass=False) # <- CHANGE THIS TO TRUE
## Calculate metrics
# First, calculate the number of dives per day for each site
inverts_daily_dive_numbers_df = determine_number_of_dives_per_period(pre_processed_inverts_df, period)
# Calculate metrics
inverts_results_df = calculate_inverts_metrics(
    pre_processed_inverts_df, inverts_daily_dive_numbers_df, period, include_biomass=False
) # <- CHANGE THIS TO TRUE
## Save results to CSV
save_site_dataframes(inverts_results_df, period, group="inverts")

#-------------------------------------------------------------------------------------------
### SUBS
## Read in survey data 
all_subs_survey_data_df = pd.read_csv(
    "data/input/DBMCP_Subs_2017-08-01_2025-05-31.csv"
)
## Pre-process survey data
pre_processed_subs_df = pre_process_data(all_subs_survey_data_df, group="subs")

## Calculate metrics
# First, calculate the number of dives per day for each site
subs_daily_dive_numbers_df = determine_number_of_dives_per_period(pre_processed_subs_df, period)
# Calculate metrics
subs_results_df = calculate_subs_metrics(
    pre_processed_subs_df, subs_daily_dive_numbers_df, period
)
## Save results to CSV
save_site_dataframes(subs_results_df, period, group="subs")
