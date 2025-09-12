#!/usr/bin/env python3
"""
Debug script to investigate commercial biomass calculation for Basak Can-Unsang MPA
"""

import pandas as pd
from pre_processing import pre_process_data
from utils import determine_number_of_dives_per_period, create_daily_df
from fish_and_inverts_shared_metrics import calculate_biomass

def debug_basak_commercial_biomass():
    print("=== DEBUGGING COMMERCIAL BIOMASS CALCULATION FOR BASAK CAN-UNSANG MPA ===\n")
    
    # Read in survey data
    print("1. Reading survey data...")
    all_fish_survey_data_df = pd.read_csv("data/input/DBMCP_Fish_2017-08-01_2025-08-31.csv")
    print(f"   Total survey records: {len(all_fish_survey_data_df)}")
    
    # Pre-process survey data
    print("\n2. Pre-processing survey data...")
    pre_processed_fish_df = pre_process_data(all_fish_survey_data_df, group="fish")
    print(f"   Pre-processed records: {len(pre_processed_fish_df)}")
    
    # Create daily dataframe
    print("\n3. Creating daily dataframe...")
    daily_fish_data_df = create_daily_df(pre_processed_fish_df, "fish")
    print(f"   Daily records: {len(daily_fish_data_df)}")
    
    # Calculate biomass
    print("\n4. Calculating biomass...")
    daily_fish_data_df = calculate_biomass(daily_fish_data_df, "data/constants/biomass_coeffs_fish.csv")
    print(f"   Records with biomass: {len(daily_fish_data_df)}")
    
    # Add periods
    print("\n5. Adding seasonal periods...")
    from utils import add_periods
    daily_fish_data_df = add_periods(daily_fish_data_df, "seasonal")
    
    # Filter for Basak Can-Unsang MPA
    print("\n6. Filtering for Basak Can-Unsang MPA...")
    basak_data = daily_fish_data_df[daily_fish_data_df["Site"] == "Basak Can-Unsang MPA"]
    print(f"   Basak records: {len(basak_data)}")
    
    # Filter for 2025 data
    print("\n7. Filtering for 2025 data...")
    basak_2025 = basak_data[basak_data["Period"].isin(["Spring 2025", "Summer 2025"])]
    print(f"   Basak 2025 records: {len(basak_2025)}")
    print(f"   Periods found: {basak_2025['Period'].unique()}")
    
    # Read commercial fish names
    print("\n8. Reading commercial fish names...")
    commercial_fish_names = (
        pd.read_csv("data/constants/commercial_fish.csv", header=None)
        .squeeze()
        .tolist()
    )
    print(f"   Commercial fish species: {len(commercial_fish_names)}")
    print(f"   First 10: {commercial_fish_names[:10]}")
    
    # Filter for commercial fish
    print("\n9. Filtering for commercial fish...")
    commercial_basak_2025 = basak_2025[basak_2025["Species"].isin(commercial_fish_names)]
    print(f"   Commercial fish records: {len(commercial_basak_2025)}")
    
    if len(commercial_basak_2025) > 0:
        print("\n10. Commercial fish species found:")
        species_counts = commercial_basak_2025["Species"].value_counts()
        print(species_counts)
        
        print("\n11. Commercial biomass by period:")
        commercial_biomass_by_period = (
            commercial_basak_2025.groupby("Period")["Total Biomass"]
            .sum()
            .reset_index()
        )
        commercial_biomass_by_period["Commercial Biomass (kg)"] = commercial_biomass_by_period["Total Biomass"] / 1000
        print(commercial_biomass_by_period)
        
        # Calculate dive numbers
        print("\n12. Calculating dive numbers...")
        dive_numbers_df = determine_number_of_dives_per_period(pre_processed_fish_df, "seasonal")
        basak_dives = dive_numbers_df[dive_numbers_df.index.get_level_values("Site") == "Basak Can-Unsang MPA"]
        print("   Dive numbers for Basak Can-Unsang MPA:")
        for period in ["Spring 2025", "Summer 2025"]:
            if (period, "Basak Can-Unsang MPA") in dive_numbers_df.index:
                dives = dive_numbers_df.loc[(period, "Basak Can-Unsang MPA")]
                print(f"     {period}: {dives} dives")
        
        # Calculate commercial biomass density
        print("\n13. Calculating commercial biomass density...")
        for _, row in commercial_biomass_by_period.iterrows():
            period = row["Period"]
            commercial_biomass_kg = row["Commercial Biomass (kg)"]
            if (period, "Basak Can-Unsang MPA") in dive_numbers_df.index:
                dives = dive_numbers_df.loc[(period, "Basak Can-Unsang MPA")]
                density = commercial_biomass_kg / dives
                print(f"     {period}: {commercial_biomass_kg:.2f} kg ÷ {dives} dives = {density:.2f}")
    
    else:
        print("\n10. NO COMMERCIAL FISH FOUND for Basak Can-Unsang MPA in 2025!")
        print("   This explains why the commercial biomass density is so low.")
        
        # Check what species are actually present
        print("\n11. Species present in Basak Can-Unsang MPA 2025:")
        species_present = basak_2025["Species"].value_counts()
        print(species_present)
        
        # Check for potential mismatches
        print("\n12. Checking for potential species name mismatches...")
        all_species = set(basak_2025["Species"].unique())
        commercial_species = set(commercial_fish_names)
        
        print(f"   Total species in data: {len(all_species)}")
        print(f"   Commercial species in list: {len(commercial_species)}")
        print(f"   Overlap: {len(all_species.intersection(commercial_species))}")
        
        # Find potential matches
        potential_matches = []
        for data_species in all_species:
            for comm_species in commercial_species:
                if data_species.lower() in comm_species.lower() or comm_species.lower() in data_species.lower():
                    potential_matches.append((data_species, comm_species))
        
        if potential_matches:
            print("\n   Potential species name matches:")
            for data_species, comm_species in potential_matches:
                print(f"     '{data_species}' <-> '{comm_species}'")

if __name__ == "__main__":
    debug_basak_commercial_biomass()
