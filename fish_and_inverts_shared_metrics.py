import pandas as pd

def calculate_biomass(daily_data_df: pd.DataFrame, biomass_coeffs_file_url: str) -> pd.DataFrame:
    """
    Calculate the biomass per creature in the dataset.

    Parameters:
    df (pd.DataFrame): The DataFrame containing creature categry and size data per site per day

    Returns:
    pd.DataFrame: Input dataframe appended with the biomass that each creature row contributes
    """
    # Read in biomass coefficients
    biomass_coeffs = pd.read_csv(
        biomass_coeffs_file_url, index_col="Species"
    )

    # Replace the lambda function with a nested for loop to calculate biomass
    biomass_values = []
    for _, row in daily_data_df.iterrows():
        coeff_a = biomass_coeffs.loc[row["Species"]]["Coeff_a"]
        coeff_b = biomass_coeffs.loc[row["Species"]]["Coeff_b"]
        biomass = row["Total"] * coeff_a * (row["Size"] ** coeff_b)
        biomass_values.append(biomass)

    daily_data_df["Total Biomass"] = biomass_values

    return daily_data_df

def calculate_total_count_and_density(daily_survey_data_df: pd.DataFrame, results_df: pd.DataFrame, dives_df: pd.DataFrame
) -> pd.DataFrame:
    """
    Calculate the total creature count and total density for each unique combination of Period and Site.

    Parameters:
    daily_survey_data_df (pd.DataFrame): The DataFrame containing creature data.
    results_df (pd.DataFrame): The DataFrame containing the number of dives per day for each site.

    Returns:
    pd.DataFrame: A DataFrame with Period, Site, Total Creature]sh Count, and Total Density.
    """
    # Calculate total creature count per site per day
    total_count = (
        daily_survey_data_df.groupby(["Period", "Site"])["Total"]
        .sum()
        .reset_index()
        .rename(columns={"Total": "Total Count"})
    )

    # Calculate total density by dividing total creature count by the number of dives
    total_count["Total Density"] = total_count.apply(
        lambda row: row["Total Count"] / dives_df.loc[(row["Period"], row["Site"])],
        axis=1,
    )
    results_df["Total Density"] = total_count["Total Density"]
    return results_df

def calculate_commercial_count_and_density(daily_fish_data_df: pd.DataFrame, results_df: pd.DataFrame, dives_df: pd.DataFrame
) -> pd.DataFrame:
    """
    Calculate the total fish count and total density for each unique combination of Period and Site.

    Parameters:
    daily_fish_data_df (pd.DataFrame): The DataFrame containing fish data.
    results_df (pd.DataFrame): The DataFrame containing the number of dives per day for each site.

    Returns:
    pd.DataFrame: A DataFrame with Period, Site, Total Fish Count, and Total Density.
    """
    # Read in commercial fish names
    commercial_fish_names = (
        pd.read_csv("data/constants/commercial_fish.csv", header=None)
        .squeeze()
        .tolist()
    )
    # Count total fish per site per day that are commercial
    commercial_count = (
        daily_fish_data_df[daily_fish_data_df["Species"].isin(commercial_fish_names)]
        .groupby(["Period", "Site"])["Total"]
        .sum()
        .reset_index()
        .rename(columns={"Total": "Commercial Count"})
    )

    # Calculate commercial density by dividing total fish count by the number of dives
    commercial_count["Commercial Density"] = commercial_count.apply(
        lambda row: row["Commercial Count"] / dives_df.loc[(row["Period"], row["Site"])],
        axis=1,
    )
    results_df["Commercial Density"] = commercial_count["Commercial Density"]
    return results_df

def calculate_total_biomass_and_density(daily_survey_data_df: pd.DataFrame, results_df: pd.DataFrame, dives_df: pd.DataFrame
) -> pd.DataFrame:
    """
    Calculate the total and normalised biomass and commercial biomass for each unique 
    combination of Period and Site. Divide by 1000

    Parameters:
    daily_survey_data_df (pd.DataFrame): The DataFrame containing creature data.
    results_df (pd.DataFrame): The DataFrame containing the number of dives per day for each site.

    Returns:
    pd.DataFrame: A DataFrame with Period, Site, Total Biomass, and Total Density.
    """
    # Calculate total biomass per site per day
    total_biomass = (
        daily_survey_data_df.groupby(["Period", "Site"])["Total Biomass"]
        .sum()
        .reset_index()
        .rename(columns={"Total Biomass": "Total Biomass"})
    )
    total_biomass["Total Biomass"] = total_biomass["Total Biomass"] / 1000  # Convert from g/ha^2 to g/m^2 

    # Calculate total biomass density by dividing total biomass by the number of dives
    total_biomass["Total Biomass Density"] = total_biomass.apply(
        lambda row: row["Total Biomass"] / dives_df.loc[(row["Period"], row["Site"])],
        axis=1,
    )
    results_df["Total Biomass Density"] = total_biomass["Total Biomass Density"]
    return results_df


def calculate_commercial_biomass(
    daily_fish_data_df: pd.DataFrame, results_df: pd.DataFrame, dives_df: pd.DataFrame
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

    commercial_biomass["Commercial Biomass"] = commercial_biomass["Commercial Biomass"] / 1000  # Convert to kg

    # Calculate commercial density by dividing total fish count by the number of dives
    commercial_biomass["Commercial Biomass Density"] = commercial_biomass.apply(
        lambda row: row["Commercial Biomass"] / dives_df.loc[(row["Period"], row["Site"])],
        axis=1,
    )
    
    results_df["Commercial Biomass Density"] = commercial_biomass["Commercial Biomass Density"]
    return results_df


def calculate_herbivore_density(
    daily_survey_data_df: pd.DataFrame,
    results_df: pd.DataFrame,
    dives_df: pd.DataFrame,
    group: str
) -> pd.DataFrame:
    """
    Calculate the total herbivore density for each unique combination of Period and Site.

    Parameters:
    daily_survey_data_df (pd.DataFrame): The DataFrame containing fish data.
    herbivores (list): A list of species names considered herbivores.
    dives_df (pd.DataFrame): The DataFrame containing the number of dives per day for each site.
    group (str): Either fish or inverts, used to determine the file path for herbivore fish names.

    Returns:
    pd.DataFrame: A DataFrame with Period, Site, and the summed herbivore density.
    """
    herbivores = (
        pd.read_csv(f"data/constants/herbivore_{group}.csv", header=None).loc[:,0].tolist()
    )
    # Calculate herbivore total counts per site per day
    herbivore_density = (
        daily_survey_data_df[daily_survey_data_df["Species"].isin(herbivores)]
        .groupby(["Period", "Site"])["Total"]
        .sum()
        .reset_index()
        .rename(columns={"Total": "Herbivore Density"})
    )

    # Divide Herbivore total counts by the number of dives to get Herbivore Density
    herbivore_density["Herbivore Density"] = herbivore_density.apply(
        lambda row: row["Herbivore Density"]
        / dives_df.loc[(row["Period"], row["Site"])],
        axis=1,
    )

    return pd.merge(herbivore_density, results_df, "right").fillna(0)


def calculate_carnivore_density(
    daily_survey_data_df: pd.DataFrame,
    results_df: pd.DataFrame,
    dives_df: pd.DataFrame,
    group: str
) -> pd.DataFrame:
    carnivores = (
        pd.read_csv(f"data/constants/carnivore_{group}.csv", header=None).loc[:,0].tolist()
    )
    carnivore_density = (
        daily_survey_data_df[daily_survey_data_df["Species"].isin(carnivores)]
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
    return pd.merge(carnivore_density, results_df, "right").fillna(0)


def calculate_omnivore_density(
    daily_survey_data_df: pd.DataFrame,
    results_df: pd.DataFrame,
    dives_df: pd.DataFrame,
    group: str
) -> pd.DataFrame:
    omnivores = (
        pd.read_csv(f"data/constants/omnivore_{group}.csv", header=None).loc[:,0].tolist()
    )
    omnivore_density = (
        daily_survey_data_df[daily_survey_data_df["Species"].isin(omnivores)]
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
    return pd.merge(omnivore_density, results_df, "right").fillna(0)


def calculate_detritivore_density(
    daily_survey_data_df: pd.DataFrame,
    results_df: pd.DataFrame,
    dives_df: pd.DataFrame,
    group: str
) -> pd.DataFrame:
    detritivores = (
        pd.read_csv(f"data/constants/detritivore_{group}.csv", header=None)
        .loc[:,0].tolist()
    )
    detritivore_density = (
        daily_survey_data_df[daily_survey_data_df["Species"].isin(detritivores)]
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
    return pd.merge(detritivore_density, results_df, "right").fillna(0)


def calculate_corallivore_density(
    daily_survey_data_df: pd.DataFrame,
    results_df: pd.DataFrame,
    dives_df: pd.DataFrame,
    group: str
) -> pd.DataFrame:
    corallivores = pd.read_csv(f"data/constants/corallivore_{group}.csv", header=None).loc[:,0].tolist()
    corallivore_density = (
        daily_survey_data_df[daily_survey_data_df["Species"].isin(corallivores)]
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
    return pd.merge(corallivore_density, results_df, "right").fillna(0)
