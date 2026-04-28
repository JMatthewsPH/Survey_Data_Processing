#!/bin/bash
# Script to run tests with various options

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}=====================================${NC}"
echo -e "${BLUE}Survey Data Processing Test Runner${NC}"
echo -e "${BLUE}=====================================${NC}"
echo ""

# Check if pytest is installed
if ! command -v pytest &> /dev/null; then
    echo -e "${RED}Error: pytest is not installed${NC}"
    echo "Install it with: pip install pytest pytest-cov"
    exit 1
fi

# Parse command line arguments
case "$1" in
    "all"|"")
        echo -e "${GREEN}Running all tests...${NC}"
        pytest tests/ -v
        ;;
    "fish")
        echo -e "${GREEN}Running fish metrics tests...${NC}"
        pytest tests/test_fish_metrics.py -v
        ;;
    "inverts")
        echo -e "${GREEN}Running invertebrate metrics tests...${NC}"
        pytest tests/test_invert_metrics.py -v
        ;;
    "subs")
        echo -e "${GREEN}Running substrate metrics tests...${NC}"
        pytest tests/test_subs_metrics.py -v
        ;;
    "integration")
        echo -e "${GREEN}Running integration tests...${NC}"
        pytest tests/test_integration.py -v
        ;;
    "coverage")
        echo -e "${GREEN}Running all tests with coverage report...${NC}"
        pytest tests/ --cov=. --cov-report=html --cov-report=term
        echo ""
        echo -e "${GREEN}Coverage report generated in htmlcov/index.html${NC}"
        ;;
    "quick")
        echo -e "${GREEN}Running quick test suite (no integration)...${NC}"
        pytest tests/ -v -k "not integration"
        ;;
    *)
        echo -e "${RED}Unknown option: $1${NC}"
        echo ""
        echo "Usage: ./run_tests.sh [option]"
        echo ""
        echo "Options:"
        echo "  all         - Run all tests (default)"
        echo "  fish        - Run only fish metrics tests"
        echo "  inverts     - Run only invertebrate metrics tests"
        echo "  subs        - Run only substrate metrics tests"
        echo "  integration - Run only integration tests"
        echo "  coverage    - Run all tests with coverage report"
        echo "  quick       - Run quick tests (excluding integration)"
        exit 1
        ;;
esac

# Capture exit code
exit_code=$?

echo ""
if [ $exit_code -eq 0 ]; then
    echo -e "${GREEN}✓ All tests passed!${NC}"
else
    echo -e "${RED}✗ Some tests failed${NC}"
fi

exit $exit_code
