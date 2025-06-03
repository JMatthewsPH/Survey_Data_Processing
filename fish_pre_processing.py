import pandas as pd


def pre_process_fish_data(all_fish_survey_data_df: pd.DataFrame) -> pd.DataFrame:
    """
    Process the fish data to:
    - remove diver/observer names
    - remove time survey was recorded from date column
    - remove invalid surveys and then survey status column
    - remove fish of size >120 (turtles, whom aren't accounted for in metrics)
    - average the size range
    - ensure Date column is in datetime format

    Parameters:
    all_fish_survey_data_df (pd.DataFrame): The DataFrame containing all fish data.

    Returns:
    pd.DataFrame: The processed DataFrame of all fish data ready for metrics
    to be calculated.
    """
    # Remove diver/observer names
    if {"Observer_name_1", "Observer_name_2"}.issubset(all_fish_survey_data_df.columns):
        all_fish_survey_data_df.drop(
            ["Observer_name_1", "Observer_name_2"], axis=1, inplace=True
        )

    # Remove time survey was recorded from date column
    all_fish_survey_data_df["Date"] = pd.to_datetime(
        all_fish_survey_data_df["Date"]
    ).dt.floor("D")

    # Remove invalid surveys then drop column as it's no longer needed
    if "Survey_Status" in all_fish_survey_data_df.columns:
        all_fish_survey_data_df = all_fish_survey_data_df[
            all_fish_survey_data_df["Survey_Status"] == 1
        ]
        all_fish_survey_data_df.drop(["Survey_Status"], axis=1, inplace=True)
        # 108471 is number of valid surveys 

    # Remove surveys of fish size >120
    all_fish_survey_data_df = all_fish_survey_data_df[
        all_fish_survey_data_df["Size"] != ">120"
    ]
    # 108444 after removing 27 >120 surveys

    # Average the size range
    size_list = [all_fish_survey_data_df["Size"].str.split("-")]
    average_size_list = []
    for row in size_list:
        for sizes in row:
            float_sizes = [float(i) for i in sizes]
            average_size_list.append(sum(float_sizes) / 2)
    all_fish_survey_data_df["Size"] = average_size_list
    return all_fish_survey_data_df


def check_all_constants_exist(all_fish_survey_data_df: pd.DataFrame) -> None:
    """
    Check that all constants used in the fish metrics calculations exist.
    If any are missing, raise an error.
    """
    # Read in constants
    constants = [
        # "biomass_coeffs.csv",
        "corallivore_fish.csv",
        "detritivore_fish.csv",
        "herbivore_fish.csv",
        "omnivore_fish.csv",
        "carnivore_fish.csv",
    ]
    all_constants = []
    for constant in constants:
        constant_list = pd.read_csv(f"data/constants/{constant}",header=None).iloc[:,0].to_list()
        all_constants.extend(constant_list)
    
    # Get all unique species in the fish survey data
    unique_species = all_fish_survey_data_df["Species"].unique()
    # Check if all species in the fish survey data exist as constants
    missing_species = list(set(unique_species) - set(all_constants))
    if missing_species:
        raise ValueError(
            f"The following species in the fish survey data are not in the species lists: {missing_species}"
        )
    print("All constants exist in the fish survey data.")



