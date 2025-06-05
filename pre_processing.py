import pandas as pd


def pre_process_data(survey_data_df: pd.DataFrame) -> pd.DataFrame:
    """
    Process survey data to:
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
    if {"Observer_name_1", "Observer_name_2"}.issubset(survey_data_df.columns):
        survey_data_df.drop(
            ["Observer_name_1", "Observer_name_2"], axis=1, inplace=True
        )

    # Remove time survey was recorded from date column
    survey_data_df["Date"] = pd.to_datetime(
        survey_data_df["Date"]
    ).dt.floor("D")

    # Remove invalid surveys then drop column as it's no longer needed
    if "Survey_Status" in survey_data_df.columns:
        survey_data_df = survey_data_df[
            survey_data_df["Survey_Status"] == 1
        ]
        survey_data_df.drop(["Survey_Status"], axis=1, inplace=True)

    # Remove surveys of fish size >120
    survey_data_df = survey_data_df[
        survey_data_df["Size"] != ">120"
    ]

    # Average the size range
    size_list = [survey_data_df["Size"].str.split("-")]
    average_size_list = []
    for row in size_list:
        for sizes in row:
            float_sizes = [float(i) for i in sizes]
            average_size_list.append(sum(float_sizes) / 2)
    survey_data_df["Size"] = average_size_list

    # Remove redundant Diver count columns (Total includes the total for both)
    survey_data_df.drop(["Diver_1_count", "Diver_2_count"], axis=1, inplace=True)
    return survey_data_df


def check_all_constants_exist_for_fish(survey_data_df: pd.DataFrame) -> None:
    """
    Check that all constants used in the fish metrics calculations exist.
    If any are missing, raise an error.
    """
    # Get all unique species in the survey data
    unique_species = survey_data_df["Species"].unique()

    # Read in constants
    consumer_constants = [
        "corallivore_fish.csv",
        "detritivore_fish.csv",
        "herbivore_fish.csv",
        "omnivore_fish.csv",
        "carnivore_fish.csv"
    ]
    all_constants = []
    for constant in consumer_constants:
        constant_list = pd.read_csv(f"data/constants/{constant}",header=None).iloc[:,0].to_list()
        all_constants.extend(constant_list)
    
    # Check all species in the survey data appear in the consumer constant CSV files
    missing_species = list(set(unique_species) - set(all_constants))
    if missing_species:
        raise ValueError(
            f"The following fish species in the survey data are not any of the consumer lists: {missing_species}"
        )
    else:
        print("All consumer constants exist for fish in the survey data.")
        
    # Check we have biomass coefficients for all species
    biomass_coeffs = pd.read_csv("data/constants/biomass_coeffs_fish.csv", index_col="Species")
    missing_biomass_coeffs = list(set(unique_species) - set(biomass_coeffs.index))
    if missing_biomass_coeffs:
        raise ValueError(
            f"The following fish species in the survey data are missing biomass coefficients: {missing_biomass_coeffs}"
        )
    else:
        print("All fish species in the survey data have biomass coefficients.")


def check_all_constants_exist_for_inverts(survey_data_df: pd.DataFrame) -> None:
    """
    Check that all constants used in the inverts metrics calculations exist.
    If any are missing, raise an error.
    """
    # Get all unique species in the survey data
    unique_species = survey_data_df["Species"].unique()

    # Read in constants
    consumer_constants = [
        "corallivore_inverts.csv",
        "detritivore_inverts.csv",
        "herbivore_inverts.csv",
        "omnivore_inverts.csv",
        "carnivore_inverts.csv",
    ]
    all_constants = []
    for constant in consumer_constants:
        constant_list = pd.read_csv(f"data/constants/{constant}",header=None).iloc[:,0].to_list()
        all_constants.extend(constant_list)
    
    # Check all species in the survey data appear in the consumer constant CSV files
    missing_species = list(set(unique_species) - set(all_constants))
    if missing_species:
        raise ValueError(
            f"The following invertebrate species in the survey data are not any of the consumer lists: {missing_species}"
        )
    else:
        print("All consumer constants exists for invertebrates in the survey data.")
        
    # Check we have biomass coefficients for all species
    biomass_coeffs = pd.read_csv("data/constants/biomass_coeffs_inverts.csv", index_col="Species")
    missing_biomass_coeffs = list(set(unique_species) - set(biomass_coeffs.index))
    if missing_biomass_coeffs:
        raise ValueError(
            f"The following invertebrate species in the survey data are missing biomass coefficients: {missing_biomass_coeffs}"
        )
    else:
        print("All invertebrate species in the survey data have biomass coefficients.")


