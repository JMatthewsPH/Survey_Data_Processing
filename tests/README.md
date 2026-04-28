# Test Suite for Survey Data Processing

This directory contains comprehensive tests for the marine survey data processing pipeline.

## Directory Structure

```
tests/
├── conftest.py              # Pytest configuration and shared fixtures
├── test_fish_metrics.py     # Tests for fish metrics calculations
├── test_invert_metrics.py   # Tests for invertebrate metrics calculations
├── test_subs_metrics.py     # Tests for substrate metrics calculations
├── test_statistics.py       # Tests for statistics calculcations on computed metrics
├── test_full_pipeline.py    # End-to-end integration tests for each set of metrics
├── test_data/               # Test data directory
│   ├── input/              # Sample CSV files for testing
│   │   ├── test_fish.csv
│   │   ├── test_inverts.csv
│   │   └── test_substrates.csv
│   └── constants/          # Test constants files
│       ├── biomass_coeffs_fish.csv
│       ├── biomass_coeffs_inverts.csv
│       ├── commercial_fish.csv
│       ├── herbivore_fish.csv
│       ├── carnivore_fish.csv
│       └── ... (other trophic group files)
└── README.md               # This file
```

## Test Data

The test data includes minimal but realistic samples for one season:

- **Test Site A**: 2 surveys on different dates (March 1 and March 2, 2024)
- **Test Site B**: 1 survey (March 5, 2024)

Each dataset includes:

- Multiple species with varying counts and sizes
- Inverts and fish in all of the different trophic groups (herbivores, carnivores, omnivores, etc.)
- Hard and soft coral with bleaching status
- Commercial and non-commercial species

## Running Tests

### Dependencies

- pytest

### Run All Tests

```bash
# From the project root directory
pytest tests/

# With verbose output
pytest tests/ -v

# With coverage report
pytest tests/ --cov=. --cov-report=html
```

### Run Specific Test Files

```bash
# Test only fish metrics
pytest tests/test_fish_metrics.py -v

# Test only invertebrate metrics
pytest tests/test_invert_metrics.py -v

# Test only substrate metrics
pytest tests/test_subs_metrics.py -v

# Test only integration tests
pytest tests/test_integration.py -v
```

### Run Specific Test Classes or Methods

```bash
# Run a specific test class
pytest tests/test_fish_metrics.py::TestFishBiomassCalculation -v

# Run a specific test method
pytest tests/test_fish_metrics.py::TestFishBiomassCalculation::test_biomass_calculation_values -v
```
