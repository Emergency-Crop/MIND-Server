#!/bin/bash
set -e

echo "Installing dependencies with Poetry..."
poetry install --no-root

echo "Setup complete."
