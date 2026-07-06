"""
Pytest configuration and shared fixtures for testing survey data processing.
"""

import os
import sys
from pathlib import Path

import pandas as pd
import pytest

# Add the parent directory to the path so we can import the modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from pre_processing import pre_process_data


@pytest.fixture
def test_data_dir():
    """Return the path to the test data directory."""
    return Path(__file__).parent / "test_data"


@pytest.fixture
def test_constants_dir(test_data_dir):
    """Return the path to the test constants directory."""
    return test_data_dir / "constants"


@pytest.fixture
def raw_fish_data(test_data_dir):
    """Load raw fish survey data."""
    return pd.read_csv(test_data_dir / "input" / "test_fish.csv")


@pytest.fixture
def raw_invert_data(test_data_dir):
    """Load raw invertebrate survey data."""
    return pd.read_csv(test_data_dir / "input" / "test_inverts.csv")


@pytest.fixture
def raw_subs_data(test_data_dir):
    """Load raw substrate survey data."""
    return pd.read_csv(test_data_dir / "input" / "test_substrates.csv")


@pytest.fixture
def preprocessed_fish_data(raw_fish_data):
    """Load and preprocess fish data."""
    return pre_process_data(raw_fish_data, group="fish")


@pytest.fixture
def preprocessed_invert_data(raw_invert_data):
    """Load and preprocess invertebrate data."""
    return pre_process_data(raw_invert_data, group="inverts")


@pytest.fixture
def preprocessed_subs_data(raw_subs_data):
    """Load and preprocess substrate data."""
    return pre_process_data(raw_subs_data, group="subs")


@pytest.fixture(autouse=True)
def set_test_constants_path(test_constants_dir, monkeypatch):
    """
    Automatically set the constants path for all tests.
    This modifies the path used by the functions to load constants files.
    """
    # Change working directory to tests directory for relative imports
    original_cwd = Path.cwd()
    test_root = Path(__file__).parent.parent
    monkeypatch.chdir(test_root)

    yield

    # Restore original working directory
    monkeypatch.chdir(original_cwd)


@pytest.fixture
def redirect_constants_to_test_data(monkeypatch):
    """
    Fixture that redirects pd.read_csv calls from data/constants/ to tests/test_data/constants/.
    Use this fixture in tests that need to load constants from test data.
    """
    original_read_csv = pd.read_csv

    def mock_read_csv(filepath, *args, **kwargs):
        if isinstance(filepath, str) and filepath.startswith("data/constants/"):
            filepath = filepath.replace("data/constants/", "tests/test_data/constants/")
        return original_read_csv(filepath, *args, **kwargs)

    monkeypatch.setattr(pd, "read_csv", mock_read_csv)
    return mock_read_csv
