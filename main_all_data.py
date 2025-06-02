import pandas as pd
from fish_pre_processing import clean_all_fish_data, create_daily_fish_df
from utils import (
    determine_number_of_dives_per_period,
    prepare_results_df,
    save_site_dataframes,
)
from fish_metrics import (
    calculate_commercial_biomass,
    calculate_herbivore_density,
    calculate_carnivore_density,
    calculate_omnivore_density,
    calculate_detritivore_density,
    calculate_corallivore_density,
)

# Read in the all fish survey data
all_fish_survey_data_df = pd.read_csv("data/DBMCP_Fish_2017-08-01_2025-05-10_ALL.csv")
print(all_fish_survey_data_df.head())
print(len(all_fish_survey_data_df))

# Pre-process the fish data to remove diver names, invalid surveys and prepare
all_fish_survey_data_df = clean_all_fish_data(all_fish_survey_data_df)
print(len(all_fish_survey_data_df))
print(all_fish_survey_data_df.head())

# Calculate the number of dives per day for each site
daily_dive_numbers_df = determine_number_of_dives_per_period(all_fish_survey_data_df)
print(daily_dive_numbers_df.head(20))

# Create dataframe that contains data at fish (category and size) level for each dive site per day
fish_daily_site_data_df = create_daily_fish_df(all_fish_survey_data_df)
print(fish_daily_site_data_df.head())
fish_daily_site_data_df.to_csv("data/last_season_fish_daily_site_data.csv", index=False)

# Use daily fish dataframe to calculate metrics
daily_fish_results_df = prepare_results_df(fish_daily_site_data_df)
daily_fish_results_df = calculate_commercial_biomass(
    fish_daily_site_data_df, daily_fish_results_df
)
daily_fish_results_df = calculate_herbivore_density(
    fish_daily_site_data_df, daily_fish_results_df, daily_dive_numbers_df
)
daily_fish_results_df = calculate_carnivore_density(
    fish_daily_site_data_df, daily_fish_results_df, daily_dive_numbers_df
)
daily_fish_results_df = calculate_omnivore_density(
    fish_daily_site_data_df, daily_fish_results_df, daily_dive_numbers_df
)
daily_fish_results_df = calculate_detritivore_density(
    fish_daily_site_data_df, daily_fish_results_df, daily_dive_numbers_df
)
daily_fish_results_df = calculate_corallivore_density(
    fish_daily_site_data_df, daily_fish_results_df, daily_dive_numbers_df
)

save_site_dataframes(daily_fish_results_df)

# # Calculate unmatched fish species
# biomass_coeffs = pd.read_csv("data/constants/biomass_coeffs.csv", index_col="Species")
# unique_df_species = all_fish_survey_data_df["Species"].unique()

# # Find unmatched species between unique_df_species and biomass_coeffs index
# unmatched_in_unique_df_species = set(unique_df_species) - set(biomass_coeffs.index)
# unmatched_in_biomass_coeffs = set(biomass_coeffs.index) - set(unique_df_species)

# print("Unmatched in unique_df_species:", unmatched_in_unique_df_species)
# print("Unmatched in biomass_coeffs:", unmatched_in_biomass_coeffs)

# # Recreate Kiri's intermediate spreadsheet to validate
# start_date = '2024-12-03'
# end_date = '2025-02-28'
# last_season_df = all_fish_survey_data_df[
#     (all_fish_survey_data_df['Date'] >= start_date) &
#     (all_fish_survey_data_df['Date'] <= end_date)
# ]
# print(len(last_season_df))
# print(last_season_df.head())
# print(last_season_df.tail())
# last_season_df.to_csv('data/last_season_fish_survey_data_for_validation.csv', index=False)


# Calculate metrics
