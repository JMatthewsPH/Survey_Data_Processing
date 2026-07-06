# Survey Data Processing

Marine survey data processing pipeline for analyzing fish, invertebrate, and substrate metrics.

## Overview

This project processes survey collected by MCP to calculate metrics.

## Metrics Calculated

### Fish

- Total density
- Total biomass density
- Commercial density and commercial biomass density
- Food group densities: herbivore, carnivore, omnivore, detritivore, corallivore

### Invertebrates

- Total density
- Total biomass density (NOTE: this is currently not enabled)
- Food group densities: herbivore, carnivore, omnivore, detritivore, corallivore

### Substrates

- Hard coral cover percentage
- Soft coral cover percentage
- Fresh algae cover percentage
- Rubble cover percentage
- Bleaching percentage

## Project Structure

```
Survey_Data_Processing/
├── data/
│   ├── input/          # Raw survey data CSV files
│   └── constants/      # Species classification and coefficients
├── tests/              # Test suite (see tests/README.md)
│   ├── test_data/      # Sample data for testing
│   └── *.py            # Test files
    └── README.md       # README with info about the tests and running them
├── main.py             # Main processing script
├── fish_metrics.py     # Fish metric calculations
├── invert_metrics.py   # Invertebrate metric calculations
├── subs_metrics.py     # Substrate metric calculations
├── pre_processing.py   # Data preprocessing
├── utils.py            # Utility functions
├── environment.yml     # Conda environment specification
├── pytest.ini          # Test configuration
├── run_tests.sh        # Test runner (bash)
└── run_tests.py        # Test runner (python)
```

## Setup

### Create Environment

```bash
conda env create -f environment.yml -p ./env
conda activate ./env
```

## Usage

### Running the Main Pipeline

Edit `main.py` to configure:

- **Period**: Choose aggregation period
  - `"seasonal"`: Individual seasons (Spring, Summer, Autumn, Winter)
  - `"monthly"`: Monthly aggregation
  - `"biannual"`: 6-month periods (Spring/Summer: Mar-Aug, Autumn/Winter: Sep-Feb)
- **Mode**: Development or production (see below)
- **Biomass**: Include/exclude biomass calculations

## At the end of a season

Run the code with period="seasonal" at the end of each season. The MCP Data Dashboard reads in the CSV files associated to each individual site from the output/fish/seasonal/, output/inverts/seasonal/ and output/subs/seasonal/ folders.

## At the end of a 6 month period (end of Feb and end of Aug)

Run the code with period="biannual". This is for the science team to use in data analysis and report writing. They should use the CSVs for All Sites for each group, located at output/fish/biannual/All_Sites.csv, output/inverts/biannual/All_Sites.csv and output/subs/biannual/All_Sites.csv

**Development vs Production Mode:**

The pipeline supports two modes via the `DEV_MODE` flag in `main.py`:

- **Production Mode** (`DEV_MODE = False`): Automatically finds the latest data files in `data/input/` using timestamp-based detection
- **Development Mode** (`DEV_MODE = True`): Uses specific file paths defined in the `data_files` dictionary

To switch modes, simply change the `DEV_MODE` variable at the top of `main.py`. MAKE SURE TO CHANGE THIS BACK BEFORE YOU SUBMIT A PULL REQUEST.

Then run:

```bash
python main.py
```

### Running Tests

The project includes a comprehensive test suite with 75+ tests covering all metrics and utility functions.

**Quick Start:**

```bash
# Run all tests
./run_tests.sh

# Or using Python
python run_tests.py
```

**In VS Code:**

- Open the Testing view (beaker icon in sidebar)
- Tests are automatically discovered
- Click ▶️ to run tests
- See [VSCODE_TEST_SETUP.md](VSCODE_TEST_SETUP.md) for detailed instructions

**Specific Test Categories:**

```bash
./run_tests.sh fish          # Fish metrics only
./run_tests.sh inverts       # Invertebrate metrics only
./run_tests.sh subs          # Substrate metrics only
./run_tests.sh integration   # Integration tests only
./run_tests.sh coverage      # With coverage report
```

**Using pytest directly:**

```bash
pytest tests/ -v                    # All tests, verbose
pytest tests/test_fish_metrics.py   # Specific file
pytest tests/ -k "biomass"          # Tests matching keyword
```

See [tests/README.md](tests/README.md) for detailed test documentation.

## Input Data Format

### Fish and Invertebrates

CSV files with columns:

- Observer_name_1, Observer_name_2
- Date, Site, Zone, Depth
- Water_Temp, Visibility, Current
- Species, Size
- Diver_1_count, Diver_2_count, Total
- Survey_Status, Survey_ID

### Substrates

CSV files with columns:

- Observer_name_1, Observer_name_2
- Date, Site, Zone, Depth
- Water_Temp, Visibility, Current
- Group, Status
- Diver_1_count, Diver_2_count, Total
- Survey_Status, Survey_ID

## Constants Files

Located in `data/constants/`:

- `biomass_coeffs_fish.csv` - Length-weight coefficients for fish
- `biomass_coeffs_inverts.csv` - Length-weight coefficients for invertebrates
- `commercial_fish.csv` - List of commercial fish species
- `herbivore_fish.csv`, `carnivore_fish.csv`, etc. - Trophic group classifications
- Similar files for invertebrates

## Output

Results are saved to `data/output/` organized by:

- Group (fish, inverts, subs)
- Site
- Period (seasonal or monthly)

Output includes, for each metric for the group:

- Mean values for each metric
- Sample sizes (number of surveys)
- Standard Deviation
- Confidence interval bounds (95%)
- Standard errors & error bars

## Development

### Adding New Species

1. Add biomass coefficients to `biomass_coeffs_[fish|inverts].csv`
2. Add to appropriate trophic group file
3. Update test data if writing tests

### Adding New Metrics

1. Implement calculation function in appropriate metrics file
2. Add to the metric_frames list in the main calculation function
3. Update metric columns list
4. Write tests in `tests/test_[metric_type].py`
