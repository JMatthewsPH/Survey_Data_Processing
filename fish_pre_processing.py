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
    all_fish_survey_data_df.drop(
        ["Observer_name_1", "Observer_name_2"], axis=1, inplace=True
    )

    # Remove time survey was recorded from date column
    all_fish_survey_data_df["Date"] = pd.to_datetime(
        all_fish_survey_data_df["Date"]
    ).dt.floor("D")

    # Remove invalid surveys then drop column as it's no longer needed
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



