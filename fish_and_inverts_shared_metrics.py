import pandas as pd
from utils import determine_number_of_surveys_per_site_for_period


def validate_species_in_trophic_groups(daily_data_df: pd.DataFrame, group: str) -> None:
    """
    Validate that all species in the data are present in at least one trophic group CSV.

    Parameters:
    daily_data_df (pd.DataFrame): The DataFrame containing species data
    group (str): Either 'fish' or 'inverts'

    Raises:
    ValueError: If any species are not found in any trophic group CSV
    """
    # Get unique species from the data
    data_species = set(daily_data_df["Species"].unique())

    # Load all trophic group CSVs
    trophic_groups = [
        "herbivore",
        "carnivore",
        "omnivore",
        "detritivore",
        "corallivore",
    ]
    all_trophic_species = set()

    for trophic in trophic_groups:
        try:
            trophic_species = (
                pd.read_csv(f"data/constants/{trophic}_{group}.csv", header=None)
                .iloc[:, 0]
                .tolist()
            )
            all_trophic_species.update(trophic_species)
        except (FileNotFoundError, pd.errors.EmptyDataError):
            # CSV doesn't exist or is empty - skip it
            continue

    # Find species not in any trophic group
    missing_species = data_species - all_trophic_species

    if missing_species:
        raise ValueError(
            f"The following species are not found in any trophic group CSV files: {sorted(missing_species)}"
        )


def calculate_biomass(
    daily_data_df: pd.DataFrame, biomass_coeffs_file_url: str
) -> pd.DataFrame:
    """
    Calculate the biomass per creature in the dataset.

    Parameters:
    df (pd.DataFrame): The DataFrame containing creature categry and size data per site per day

    Returns:
    pd.DataFrame: Input dataframe appended with the biomass that each creature row contributes
    """
    # Read in biomass coefficients
    biomass_coeffs = pd.read_csv(biomass_coeffs_file_url, index_col="Species")

    # Replace the lambda function with a nested for loop to calculate biomass
    biomass_values = []
    for _, row in daily_data_df.iterrows():
        coeff_a = biomass_coeffs.loc[row["Species"]]["Coeff_a"]
        coeff_b = biomass_coeffs.loc[row["Species"]]["Coeff_b"]
        biomass = row["Total"] * coeff_a * (row["Size"] ** coeff_b)
        biomass_values.append(biomass)

    daily_data_df["Total Biomass"] = biomass_values

    return daily_data_df


def calculate_total_count(
    daily_survey_data_df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Calculate daily total counts for each site.
    """
    # Calculate total creature count per site per day
    total_count = (
        daily_survey_data_df.groupby(["Survey_ID", "Date", "Period", "Site"])["Total"]
        .sum()
        .reset_index()
        .rename(columns={"Total": "Total Count"})
    )

    return total_count[["Survey_ID", "Date", "Period", "Site", "Total Count"]]


def calculate_total_biomass(
    daily_survey_data_df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Calculate the daily biomass (converted to kg) for each site.
    """
    # Calculate total biomass per site per day
    total_biomass = (
        daily_survey_data_df.groupby(["Survey_ID", "Date", "Period", "Site"])[
            "Total Biomass"
        ]
        .sum()
        .reset_index()
        .rename(columns={"Total Biomass": "Total Biomass"})
    )
    total_biomass["Total Biomass"] = (
        total_biomass["Total Biomass"] / 1000
    )  # Convert from g/ha^2 to kg

    return total_biomass[["Survey_ID", "Date", "Period", "Site", "Total Biomass"]]


def calculate_herbivore_count(
    daily_survey_data_df: pd.DataFrame,
    group: str,
) -> pd.DataFrame:
    """
    Calculate the total herbivore count for each unique combination of Period and Site.

    Parameters:
    daily_survey_data_df (pd.DataFrame): The DataFrame containing fish data.
    group (str): Either fish or inverts, used to determine the file path for herbivore names.

    Returns:
    pd.DataFrame: A DataFrame with Period, Site, and the summed herbivore count.
    """
    herbivores = (
        pd.read_csv(f"data/constants/herbivore_{group}.csv", header=None)
        .loc[:, 0]
        .tolist()
    )
    # Calculate herbivore total counts per site per day
    herbivore_count = (
        daily_survey_data_df[daily_survey_data_df["Species"].isin(herbivores)]
        .groupby(["Survey_ID", "Date", "Period", "Site"])["Total"]
        .sum()
        .reset_index()
        .rename(columns={"Total": "Herbivore Count"})
    )

    return herbivore_count[["Survey_ID", "Date", "Period", "Site", "Herbivore Count"]]


def calculate_carnivore_count(
    daily_survey_data_df: pd.DataFrame,
    group: str,
) -> pd.DataFrame:
    carnivores = (
        pd.read_csv(f"data/constants/carnivore_{group}.csv", header=None)
        .loc[:, 0]
        .tolist()
    )
    carnivore_count = (
        daily_survey_data_df[daily_survey_data_df["Species"].isin(carnivores)]
        .groupby(["Survey_ID", "Date", "Period", "Site"])["Total"]
        .sum()
        .reset_index()
        .rename(columns={"Total": "Carnivore Count"})
    )
    return carnivore_count[["Survey_ID", "Date", "Period", "Site", "Carnivore Count"]]


def calculate_omnivore_count(
    daily_survey_data_df: pd.DataFrame,
    group: str,
) -> pd.DataFrame:
    omnivores = (
        pd.read_csv(f"data/constants/omnivore_{group}.csv", header=None)
        .loc[:, 0]
        .tolist()
    )
    omnivore_count = (
        daily_survey_data_df[daily_survey_data_df["Species"].isin(omnivores)]
        .groupby(["Survey_ID", "Date", "Period", "Site"])["Total"]
        .sum()
        .reset_index()
        .rename(columns={"Total": "Omnivore Count"})
    )
    return omnivore_count[["Survey_ID", "Date", "Period", "Site", "Omnivore Count"]]


def calculate_detritivore_count(
    daily_survey_data_df: pd.DataFrame,
    group: str,
) -> pd.DataFrame:
    detritivores = (
        pd.read_csv(f"data/constants/detritivore_{group}.csv", header=None)
        .loc[:, 0]
        .tolist()
    )
    detritivore_count = (
        daily_survey_data_df[daily_survey_data_df["Species"].isin(detritivores)]
        .groupby(["Survey_ID", "Date", "Period", "Site"])["Total"]
        .sum()
        .reset_index()
        .rename(columns={"Total": "Detritivore Count"})
    )
    return detritivore_count[
        ["Survey_ID", "Date", "Period", "Site", "Detritivore Count"]
    ]


def calculate_corallivore_count(
    daily_survey_data_df: pd.DataFrame,
    group: str,
) -> pd.DataFrame:
    corallivores = (
        pd.read_csv(f"data/constants/corallivore_{group}.csv", header=None)
        .loc[:, 0]
        .tolist()
    )
    corallivore_count = (
        daily_survey_data_df[daily_survey_data_df["Species"].isin(corallivores)]
        .groupby(["Survey_ID", "Date", "Period", "Site"])["Total"]
        .sum()
        .reset_index()
        .rename(columns={"Total": "Corallivore Count"})
    )
    return corallivore_count[
        ["Survey_ID", "Date", "Period", "Site", "Corallivore Count"]
    ]


def calculate_species_richness(daily_survey_data_df: pd.DataFrame):
    """
    Calculate species richness (number of unique species observed per period).
    Calculates both overall richness and depth-specific richness (Shallow, Medium, Deep).
    NOTE: this is not calculated the same way as the other metrics - it is just
    one number calculated for the entire period rather than a value calculated
    per survey with statistics calculated on it at the end.

    Parameters:
    daily_survey_data_df (pd.DataFrame): DataFrame containing survey data with Depth column.

    Returns:
    pd.DataFrame: DataFrame with overall and depth-specific species richness and
    average species richness (normalised by number of surveys) calculated per period per site.
    """
    # Calculate overall species richness (all depths combined)
    species_richness = (
        daily_survey_data_df.groupby(["Period", "Site"])["Species"]
        .nunique()
        .reset_index()
        .rename(columns={"Species": "Species Richness"})
    )

    number_of_surveys_df = determine_number_of_surveys_per_site_for_period(
        daily_survey_data_df
    )

    # Merge the number of surveys into the species richness dataframe
    species_richness = species_richness.merge(
        number_of_surveys_df, on=["Period", "Site"], how="left"
    )

    species_richness["Average Species Richness"] = (
        species_richness["Species Richness"] / species_richness["Number of Surveys"]
    )

    # Calculate depth-specific species richness
    for depth in ["Shallow", "Medium", "Deep"]:
        depth_data = daily_survey_data_df[daily_survey_data_df["Depth"] == depth]

        if len(depth_data) > 0:
            depth_richness = (
                depth_data.groupby(["Period", "Site"])["Species"]
                .nunique()
                .reset_index()
                .rename(columns={"Species": f"Species Richness {depth}"})
            )

            # Count surveys for this depth
            depth_surveys = (
                depth_data.groupby(["Period", "Site"])["Survey_ID"]
                .nunique()
                .reset_index()
                .rename(columns={"Survey_ID": f"Number of Surveys {depth}"})
            )

            # Merge depth richness
            species_richness = species_richness.merge(
                depth_richness, on=["Period", "Site"], how="left"
            )

            # Merge depth survey counts
            species_richness = species_richness.merge(
                depth_surveys, on=["Period", "Site"], how="left"
            )

            # Calculate average for this depth
            species_richness[f"Average Species Richness {depth}"] = (
                species_richness[f"Species Richness {depth}"]
                / species_richness[f"Number of Surveys {depth}"]
            )
        else:
            # If no data for this depth, add columns with NaN
            species_richness[f"Species Richness {depth}"] = pd.NA
            species_richness[f"Number of Surveys {depth}"] = pd.NA
            species_richness[f"Average Species Richness {depth}"] = pd.NA

    return species_richness
