#!/bin/bash

# 2. Log and Activate virtual environment
echo "Activating the virtual environment..."
source .venv/bin/activate
if [[ "$VIRTUAL_ENV" != "" ]]; then
    echo "Virtual environment activated: $VIRTUAL_ENV"
else
    echo "Failed to activate virtual environment."
    exit 1
fi

# 3. Upgrade pip to the latest version
pip install --upgrade pip

# 5. Create a blank .streamlit/secrets.toml.example file
mkdir -p .streamlit
touch .streamlit/secrets.toml.example