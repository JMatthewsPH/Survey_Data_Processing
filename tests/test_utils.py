"""
Tests for utility functions in utils.py
"""

import pandas as pd
import pytest
from utils import add_periods, period_sort_key


class TestAddPeriods:
    """Test the add_periods function for different period types."""

    @pytest.fixture
    def sample_dates_df(self):
        """
        Create a DataFrame with sample dates spanning multiple years and seasons.
        Includes dates from each month to test all period types.
        """
        dates = [
            # Winter 2023/2024
            "2023-12-15",  # December 2023
            "2024-01-10",  # January 2024
            "2024-02-20",  # February 2024
            # Spring 2024
            "2024-03-05",  # March 2024
            "2024-04-15",  # April 2024
            "2024-05-25",  # May 2024
            # Summer 2024
            "2024-06-10",  # June 2024
            "2024-07-20",  # July 2024
            "2024-08-30",  # August 2024
            # Autumn 2024
            "2024-09-05",  # September 2024
            "2024-10-15",  # October 2024
            "2024-11-25",  # November 2024
            # Winter 2024/2025
            "2024-12-10",  # December 2024
            "2025-01-15",  # January 2025
            "2025-02-28",  # February 2025
        ]
        return pd.DataFrame({"Date": pd.to_datetime(dates)})

    def test_monthly_periods(self, sample_dates_df):
        """Test that monthly period assignment works correctly."""
        result_df = add_periods(sample_dates_df.copy(), period="monthly")

        # Check that Period column was added
        assert "Period" in result_df.columns

        # Verify specific date mappings
        assert str(result_df.loc[0, "Period"]) == "2023-12"  # Dec 2023
        assert str(result_df.loc[3, "Period"]) == "2024-03"  # Mar 2024
        assert str(result_df.loc[6, "Period"]) == "2024-06"  # Jun 2024
        assert str(result_df.loc[9, "Period"]) == "2024-09"  # Sep 2024
        assert str(result_df.loc[12, "Period"]) == "2024-12"  # Dec 2024

        # Check we have 15 different months represented (one per date)
        assert len(result_df["Period"].unique()) == 15

    def test_seasonal_periods(self, sample_dates_df):
        """Test that seasonal period assignment works correctly."""
        result_df = add_periods(sample_dates_df.copy(), period="seasonal")

        # Check that Period column was added
        assert "Period" in result_df.columns

        # Verify Winter periods (spans two years)
        assert result_df.loc[0, "Period"] == "Winter 23/24"  # Dec 2023
        assert result_df.loc[1, "Period"] == "Winter 23/24"  # Jan 2024
        assert result_df.loc[2, "Period"] == "Winter 23/24"  # Feb 2024

        # Verify Spring 2024
        assert result_df.loc[3, "Period"] == "Spring 2024"  # Mar 2024
        assert result_df.loc[4, "Period"] == "Spring 2024"  # Apr 2024
        assert result_df.loc[5, "Period"] == "Spring 2024"  # May 2024

        # Verify Summer 2024
        assert result_df.loc[6, "Period"] == "Summer 2024"  # Jun 2024
        assert result_df.loc[7, "Period"] == "Summer 2024"  # Jul 2024
        assert result_df.loc[8, "Period"] == "Summer 2024"  # Aug 2024

        # Verify Autumn 2024
        assert result_df.loc[9, "Period"] == "Autumn 2024"  # Sep 2024
        assert result_df.loc[10, "Period"] == "Autumn 2024"  # Oct 2024
        assert result_df.loc[11, "Period"] == "Autumn 2024"  # Nov 2024

        # Verify Winter 2024/2025
        assert result_df.loc[12, "Period"] == "Winter 24/25"  # Dec 2024
        assert result_df.loc[13, "Period"] == "Winter 24/25"  # Jan 2025
        assert result_df.loc[14, "Period"] == "Winter 24/25"  # Feb 2025

        # Check we have 5 unique periods (Winter 23/24, Spring 24, Summer 24, Autumn 24, Winter 24/25)
        assert len(result_df["Period"].unique()) == 5

    def test_biannual_periods(self, sample_dates_df):
        """Test that biannual (6-month) period assignment works correctly."""
        result_df = add_periods(sample_dates_df.copy(), period="biannual")

        # Check that Period column was added
        assert "Period" in result_df.columns

        # Verify Autumn/Winter 2023/2024 (Sep-Feb)
        assert result_df.loc[0, "Period"] == "Autumn/Winter 23/24"  # Dec 2023
        assert result_df.loc[1, "Period"] == "Autumn/Winter 23/24"  # Jan 2024
        assert result_df.loc[2, "Period"] == "Autumn/Winter 23/24"  # Feb 2024

        # Verify Spring/Summer 2024 (Mar-Aug)
        assert result_df.loc[3, "Period"] == "Spring/Summer 24"  # Mar 2024
        assert result_df.loc[4, "Period"] == "Spring/Summer 24"  # Apr 2024
        assert result_df.loc[5, "Period"] == "Spring/Summer 24"  # May 2024
        assert result_df.loc[6, "Period"] == "Spring/Summer 24"  # Jun 2024
        assert result_df.loc[7, "Period"] == "Spring/Summer 24"  # Jul 2024
        assert result_df.loc[8, "Period"] == "Spring/Summer 24"  # Aug 2024

        # Verify Autumn/Winter 2024/2025 (Sep-Feb)
        assert result_df.loc[9, "Period"] == "Autumn/Winter 24/25"  # Sep 2024
        assert result_df.loc[10, "Period"] == "Autumn/Winter 24/25"  # Oct 2024
        assert result_df.loc[11, "Period"] == "Autumn/Winter 24/25"  # Nov 2024
        assert result_df.loc[12, "Period"] == "Autumn/Winter 24/25"  # Dec 2024
        assert result_df.loc[13, "Period"] == "Autumn/Winter 24/25"  # Jan 2025
        assert result_df.loc[14, "Period"] == "Autumn/Winter 24/25"  # Feb 2025

        # Check we have 3 unique periods
        assert len(result_df["Period"].unique()) == 3
        expected_periods = {
            "Autumn/Winter 23/24",
            "Spring/Summer 24",
            "Autumn/Winter 24/25",
        }
        assert set(result_df["Period"].unique()) == expected_periods


class TestPeriodSortKey:
    """Test the period_sort_key function for correct chronological sorting."""

    def test_seasonal_sort_order(self):
        """Test that seasonal periods are sorted correctly."""
        periods = [
            "Autumn 2024",
            "Winter 23/24",
            "Summer 2024",
            "Spring 2024",
            "Winter 24/25",
            "Spring 2023",
        ]
        sorted_periods = sorted(periods, key=period_sort_key)

        expected_order = [
            "Spring 2023",
            "Winter 23/24",
            "Spring 2024",
            "Summer 2024",
            "Autumn 2024",
            "Winter 24/25",
        ]
        assert sorted_periods == expected_order

    def test_biannual_sort_order(self):
        """Test that biannual periods are sorted correctly."""
        periods = [
            "Autumn/Winter 24/25",
            "Spring/Summer 23",
            "Autumn/Winter 23/24",
            "Spring/Summer 24",
        ]
        sorted_periods = sorted(periods, key=period_sort_key)

        expected_order = [
            "Spring/Summer 23",
            "Autumn/Winter 23/24",
            "Spring/Summer 24",
            "Autumn/Winter 24/25",
        ]
        assert sorted_periods == expected_order

    def test_mixed_period_types_sort(self):
        """Test sorting when mixing seasonal and biannual periods."""
        periods = [
            "Summer 2024",
            "Autumn/Winter 23/24",
            "Spring 2024",
            "Spring/Summer 24",
        ]
        sorted_periods = sorted(periods, key=period_sort_key)

        # Biannual periods should sort between corresponding seasons
        # Autumn/Winter 23/24 should come before Spring 2024
        # Spring/Summer 24 should come after Spring 2024 (0.5 vs 1)
        assert sorted_periods[0] == "Autumn/Winter 23/24"
        assert sorted_periods[1] == "Spring/Summer 24"
        assert sorted_periods[2] == "Spring 2024"
        assert sorted_periods[3] == "Summer 2024"

    def test_unrecognized_period_format(self):
        """Test that unrecognized formats are sorted to the end."""
        periods = [
            "Spring 2024",
            "InvalidFormat",
            "Summer 2024",
            "Unknown",
        ]
        sorted_periods = sorted(periods, key=period_sort_key)

        # Valid periods should come first
        assert sorted_periods[0] == "Spring 2024"
        assert sorted_periods[1] == "Summer 2024"
        # Unrecognized formats at the end (order between them doesn't matter)
        assert sorted_periods[2] in ["InvalidFormat", "Unknown"]
        assert sorted_periods[3] in ["InvalidFormat", "Unknown"]
