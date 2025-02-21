#!/bin/bash

# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate  # For Unix/Linux
# or
# .\venv\Scripts\activate  # For Windows

# Install required packages
pip install -r requirements.txt

echo "Virtual environment setup complete!"
echo "To activate:"
echo "source venv/bin/activate  # For Unix/Linux"
echo ".\venv\Scripts\activate   # For Windows"
