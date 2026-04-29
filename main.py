import pandas as pd
from fish_metrics import (
    calculate_fish_metrics,
)
from invert_metrics import (
    calculate_inverts_metrics,
)
from pre_processing import (
    check_all_constants_exist_for_fish,
    check_all_constants_exist_for_inverts,
    pre_process_data,
)
from subs_metrics import calculate_subs_metrics
from utils import (
    find_latest_data_files,
    save_site_dataframes,
)

period = "seasonal"  # seasonal or monthly

# # Automatically find the latest data files
# print("=== AUTOMATICALLY DETECTING LATEST DATA FILES ===")
# data_files = find_latest_data_files()
# print("=" * 50)

# data_files = {"inverts": "data/input/Underconstruction Benthic DECFEB.csv"}


# ### FISH

# ## Read in survey data
# if "fish" not in data_files:
#     raise FileNotFoundError("No fish data file found in data/input directory")
# all_fish_survey_data_df = pd.read_csv(data_files["fish"])

# ## Pre-process survey data
# pre_processed_fish_df = pre_process_data(all_fish_survey_data_df, group="fish")
# # Check that all constants used in the fish metrics calculations exist
# check_all_constants_exist_for_fish(pre_processed_fish_df)

# ## Calculate metrics
# # Calculate metrics
# fish_results_df = calculate_fish_metrics(
#     pre_processed_fish_df, period
# )
# ## Save results to CSV
# save_site_dataframes(fish_results_df, period, group="fish")

# -------------------------------------------------------------------------------------------
### INVERTS
## WHEN BIOMASS COEFFICIENTS BECOME AVAILABLE FOR INVERTS, YOU NEED TO CHANGE TWO THINGS BELOW
## Read in survey data
# if "inverts" not in data_files:
#     raise FileNotFoundError("No inverts data file found in data/input directory")

all_invert_survey_data_df = pd.read_csv(
    "data/input/Underconstruction Benthic DECFEB.csv"
)
# all_invert_survey_data_df = pd.read_csv(data_files["inverts"])
## Pre-process survey data
pre_processed_inverts_df = pre_process_data(all_invert_survey_data_df, group="inverts")
# Check that all constants used in the fish metrics calculations exist
check_all_constants_exist_for_inverts(
    pre_processed_inverts_df, include_biomass=False
)  # <- CHANGE THIS TO TRUE
## Calculate metrics
# Calculate metrics
inverts_results_df = calculate_inverts_metrics(
    pre_processed_inverts_df,
    period,
    include_biomass=False,
)  # <- CHANGE THIS TO TRUE
## Save results to CSV
save_site_dataframes(inverts_results_df, period, group="inverts")

# -------------------------------------------------------------------------------------------
### SUBS
## Read in survey data
if "subs" not in data_files:
    raise FileNotFoundError("No substrate data file found in data/input directory")
all_subs_survey_data_df = pd.read_csv(data_files["subs"])
## Pre-process survey data
pre_processed_subs_df = pre_process_data(all_subs_survey_data_df, group="subs")

## Calculate metrics
# Calculate metrics
subs_results_df = calculate_subs_metrics(pre_processed_subs_df, period)
## Save results to CSV
save_site_dataframes(subs_results_df, period, group="subs")
