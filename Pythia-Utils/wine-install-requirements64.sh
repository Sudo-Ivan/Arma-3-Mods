#!/bin/bash

#############################################################################
# This script will install any python dependencies that will be needed
# by any *64-bit* Pythia code, using Wine to run the Windows Python embedded
# distribution from Linux.
#
# Usage:
# 1. Drag and drop: Simply drag a requirements.txt file onto install_requirements64.sh
# 2. Command line: ./install_requirements64.sh --requirements path/to/requirements.txt
#############################################################################

# Get the script's directory
SCRIPT_DIR="$(dirname "$(readlink -f "$0")")"
interpreter="${SCRIPT_DIR}/python-310-embed-amd64"

# Function to install requirements
install_requirements() {
    local req_file="$1"

    if [ ! -f "$req_file" ]; then
        echo "Error: Requirements file not found: $req_file"
        exit 1
    fi

    echo "==============================================================================="
    echo "Installing requirements for $interpreter from \"$req_file\"..."
    echo "==============================================================================="

    # Convert Linux path to Windows path for the requirements file
    win_req_file="$(winepath -w "$req_file")"

    WINEDEBUG=-all PYTHONPATH="${interpreter}/Lib/site-packages" \
    wine "${interpreter}/python.exe" -I -m pip install --upgrade --no-warn-script-location -r "$win_req_file"

    if [ $? -ne 0 ]; then
        echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
        echo "An error happened during requirements installation. Your python environment is"
        echo "now in an undefined state!"
        echo "Fix the issues and reinstall the requirements!"
        echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
        exit 1
    fi
}

# Check if wine is installed
if ! command -v wine &> /dev/null; then
    echo "Error: Wine is not installed. Please install wine to continue."
    exit 1
fi

# Check if winepath is installed
if ! command -v winepath &> /dev/null; then
    echo "Error: winepath is not installed. Please install wine to continue."
    exit 1
fi

# Check if script is called with --requirements
if [ "$1" = "--requirements" ]; then
    if [ -z "$2" ]; then
        echo "Error: No requirements file specified after --requirements"
        echo "Usage: $0 --requirements path/to/requirements.txt"
        exit 1
    fi
    install_requirements "$2"
# Handle drag and drop case
elif [ -n "$1" ]; then
    install_requirements "$1"
else
    echo "Error: No requirements file provided"
    echo "Usage:"
    echo "  1. Drag and drop requirements.txt onto this script"
    echo "  2. $0 --requirements path/to/requirements.txt"
    exit 1
fi

echo "==============================================================================="
echo "Requirements installation completed successfully!"
echo "==============================================================================="
