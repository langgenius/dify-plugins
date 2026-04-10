#!/bin/bash
# Copyright 2026 SupraWall Contributors
# SPDX-License-Identifier: Apache-2.0

# Setup script for pre-commit hooks
# Run this once after cloning the repository

set -e

echo "Setting up pre-commit hooks..."

# Check if pre-commit is installed
if ! command -v pre-commit &> /dev/null; then
    echo "Installing pre-commit..."
    if command -v pip &> /dev/null; then
        pip install pre-commit
    elif command -v pip3 &> /dev/null; then
        pip3 install pre-commit
    else
        echo "ERROR: pip not found. Please install Python first."
        exit 1
    fi
fi

# Install the pre-commit hooks
pre-commit install
echo "✓ Pre-commit hooks installed"

# Generate secrets baseline if it doesn't exist
if [ ! -f .secrets.baseline ]; then
    echo "Generating detect-secrets baseline..."
    detect-secrets scan --all-files > .secrets.baseline || true
    echo "✓ Secrets baseline generated"
fi

echo ""
echo "Pre-commit hooks setup complete!"
echo ""
echo "To run hooks manually on all files:"
echo "  pre-commit run --all-files"
echo ""
echo "To bypass hooks (NOT RECOMMENDED):"
echo "  git commit --no-verify"
