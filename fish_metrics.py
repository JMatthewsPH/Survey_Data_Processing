import pandas as pd
from utils import prepare_results_df, add_periods


def calculate_fish_metrics(
    pre_processed_fish_data_df: pd.DataFrame,
    daily_dive_numbers_df: pd.DataFrame,
    period: str = "daily",
) -> pd.DataFrame:
    """
    Calculate various fish metrics for each unique combination of Period and Site, or aggregated by month or season.

    Parameters:
    daily_fish_data_df (pd.DataFrame): The DataFrame containing fish data.
    daily_dive_numbers_df (pd.DataFrame): The DataFrame containing the number of dives per day for each site.
    period (str): The period for aggregation. Options are "daily", "monthly", or "seasonal".

    Returns:
    pd.DataFrame: A DataFrame with aggregated metrics based on the specified period.
    """
    daily_fish_data_df = create_daily_fish_df(pre_processed_fish_data_df)
    daily_fish_data_df = add_periods(daily_fish_data_df, period)

    results_df = prepare_results_df(daily_fish_data_df)
    results_df = calculate_commercial_biomass(daily_fish_data_df, results_df)
    results_df = calculate_herbivore_density(
        daily_fish_data_df, results_df, daily_dive_numbers_df
    )
    results_df = calculate_carnivore_density(
        daily_fish_data_df, results_df, daily_dive_numbers_df
    )
    results_df = calculate_omnivore_density(
        daily_fish_data_df, results_df, daily_dive_numbers_df
    )
    results_df = calculate_detritivore_density(
        daily_fish_data_df, results_df, daily_dive_numbers_df
    )
    results_df = calculate_corallivore_density(
        daily_fish_data_df, results_df, daily_dive_numbers_df
    )

    return (
        results_df.groupby(["Period", "Site"]).sum().reset_index()
        if period != "daily"
        else results_df
    )


def calculate_commercial_biomass(
    daily_fish_data_df: pd.DataFrame, results_df: pd.DataFrame
) -> pd.DataFrame:
    """
    Calculate the total commercial biomass for each unique combination of Period and Site.

    Parameters:
    daily_fish_data_df (pd.DataFrame): The DataFrame containing fish data.
    commercial_fish_names (list): A list of species names considered commercial.

    Returns:
    pd.DataFrame: A DataFrame with Period, Site, and the summed commercial biomass.
    """
    commercial_fish_names = (
        pd.read_csv("data/constants/commercial_fish.csv", header=None)
        .squeeze()
        .tolist()
    )
    # Calculate commercial biomass per site per day
    commercial_biomass = (
        daily_fish_data_df[daily_fish_data_df["Species"].isin(commercial_fish_names)]
        .groupby(["Period", "Site"])["Total Biomass"]
        .sum()
        .reset_index()
        .rename(columns={"Total Biomass": "Commercial Biomass"})
    )

    # Add Total Biomass column back to the DataFrame
    commercial_biomass = commercial_biomass.merge(
        daily_fish_data_df.groupby(["Period", "Site"])["Total Biomass"]
        .sum()
        .reset_index(),
        on=["Period", "Site"],
        suffixes=("", "_Total"),
    )

    return pd.merge(commercial_biomass, results_df)


def calculate_herbivore_density(
    daily_fish_data_df: pd.DataFrame,
    results_df: pd.DataFrame,
    dives_df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Calculate the total herbivore density for each unique combination of Period and Site.

    Parameters:
    daily_fish_data_df (pd.DataFrame): The DataFrame containing fish data.
    herbivore_fish_names (list): A list of species names considered herbivores.
    dives_df (pd.DataFrame): The DataFrame containing the number of dives per day for each site.

    Returns:
    pd.DataFrame: A DataFrame with Period, Site, and the summed herbivore density.
    """
    herbivore_fish_names = (
        pd.read_csv("data/constants/herbivore_fish.csv", header=None).squeeze().tolist()
    )
    # Calculate herbivore density per site per day
    herbivore_density = (
        daily_fish_data_df[daily_fish_data_df["Species"].isin(herbivore_fish_names)]
        .groupby(["Period", "Site"])["Total"]
        .sum()
        .reset_index()
        .rename(columns={"Total": "Herbivore Density"})
    )

    # Divide Herbivore Density by the number of dives
    herbivore_density["Herbivore Density"] = herbivore_density.apply(
        lambda row: row["Herbivore Density"]
        / dives_df.loc[(row["Period"], row["Site"])],
        axis=1,
    )

    return pd.merge(herbivore_density, results_df)


def calculate_carnivore_density(
    daily_fish_data_df: pd.DataFrame,
    results_df: pd.DataFrame,
    dives_df: pd.DataFrame,
) -> pd.DataFrame:
    carnivore_fish_names = (
        pd.read_csv("data/constants/carnivore_fish.csv", header=None).squeeze().tolist()
    )
    carnivore_density = (
        daily_fish_data_df[daily_fish_data_df["Species"].isin(carnivore_fish_names)]
        .groupby(["Period", "Site"])["Total"]
        .sum()
        .reset_index()
        .rename(columns={"Total": "Carnivore Density"})
    )
    carnivore_density["Carnivore Density"] = carnivore_density.apply(
        lambda row: row["Carnivore Density"]
        / dives_df.loc[(row["Period"], row["Site"])],
        axis=1,
    )
    return pd.merge(carnivore_density, results_df)


def calculate_omnivore_density(
    daily_fish_data_df: pd.DataFrame,
    results_df: pd.DataFrame,
    dives_df: pd.DataFrame,
) -> pd.DataFrame:
    omnivore_fish_names = (
        pd.read_csv("data/constants/omnivore_fish.csv", header=None).squeeze().tolist()
    )
    omnivore_density = (
        daily_fish_data_df[daily_fish_data_df["Species"].isin(omnivore_fish_names)]
        .groupby(["Period", "Site"])["Total"]
        .sum()
        .reset_index()
        .rename(columns={"Total": "Omnivore Density"})
    )
    omnivore_density["Omnivore Density"] = omnivore_density.apply(
        lambda row: row["Omnivore Density"]
        / dives_df.loc[(row["Period"], row["Site"])],
        axis=1,
    )
    return pd.merge(omnivore_density, results_df)


def calculate_detritivore_density(
    daily_fish_data_df: pd.DataFrame,
    results_df: pd.DataFrame,
    dives_df: pd.DataFrame,
) -> pd.DataFrame:
    detritivore_fish_names = (
        pd.read_csv("data/constants/detritivore_fish.csv", header=None)
        .squeeze()
        .tolist()
    )
    detritivore_density = (
        daily_fish_data_df[daily_fish_data_df["Species"].isin(detritivore_fish_names)]
        .groupby(["Period", "Site"])["Total"]
        .sum()
        .reset_index()
        .rename(columns={"Total": "Detritivore Density"})
    )
    detritivore_density["Detritivore Density"] = detritivore_density.apply(
        lambda row: row["Detritivore Density"]
        / dives_df.loc[(row["Period"], row["Site"])],
        axis=1,
    )
    return pd.merge(detritivore_density, results_df)


def calculate_corallivore_density(
    daily_fish_data_df: pd.DataFrame,
    results_df: pd.DataFrame,
    dives_df: pd.DataFrame,
) -> pd.DataFrame:
    corallivore_fish_names = [
        pd.read_csv("data/constants/corallivore_fish.csv", header=None).squeeze()
    ]
    corallivore_density = (
        daily_fish_data_df[daily_fish_data_df["Species"].isin(corallivore_fish_names)]
        .groupby(["Period", "Site"])["Total"]
        .sum()
        .reset_index()
        .rename(columns={"Total": "Corallivore Density"})
    )
    corallivore_density["Corallivore Density"] = corallivore_density.apply(
        lambda row: row["Corallivore Density"]
        / dives_df.loc[(row["Period"], row["Site"])],
        axis=1,
    )
    return pd.merge(corallivore_density, results_df)


def create_daily_fish_df(all_fish_survey_data_df: pd.DataFrame) -> pd.DataFrame:
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
    aggregated_fish_df = (
        all_fish_survey_data_df.groupby(["Date", "Site", "Species", "Size"])
        .agg({"Total": "sum"})
        .reset_index()
    )
    final_daily_fish_df = calculate_biomass(aggregated_fish_df)
    return final_daily_fish_df


def calculate_biomass(daily_fish_data_df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate the biomass per fish type in the dataset.

    Parameters:
    df (pd.DataFrame): The DataFrame containing fish categry and size data per site per day

    Returns:
    pd.DataFrame: Input dataframe appended with the biomass that each fish row contributes
    """
    # Read in biomass coefficients
    biomass_coeffs = pd.read_csv(
        "data/constants/biomass_coeffs.csv", index_col="Species"
    )
    # temperorary until we get the coeffs
    species_with_no_biomass_coeffs = [
        "Grouper - Brown-Marbled",
        "Grouper - Barramundi",
        "Sea Ray - Ribbontail",
        "Sea Ray - Stingray",
        "Rabbitfish - White Spotted",
        "Angelfish - Two-Spined",
        "Shark - Whale Shark",
        "Sea Ray - Other",
        "Long Jawed Mackerel",
        "Emperor - Orange-Striped",
        "Parrotfish - Humphead",
        "Snapper - One-Spot",
    ]

    # Replace the lambda function with a nested for loop to calculate biomass
    biomass_values = []
    for _, row in daily_fish_data_df.iterrows():
        if row["Species"] not in species_with_no_biomass_coeffs:
            coeff_a = biomass_coeffs.loc[row["Species"]]["Coeff_a"]
            coeff_b = biomass_coeffs.loc[row["Species"]]["Coeff_b"]
            biomass = row["Total"] * coeff_a * (row["Size"] ** coeff_b)
        else:
            biomass = 0
        biomass_values.append(biomass)

    daily_fish_data_df["Total Biomass"] = biomass_values

    return daily_fish_data_df
