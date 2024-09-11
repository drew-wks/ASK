#!/bin/bash

# 1. Create virtual environment
python3 -m venv venv

# 2. Log and Activate virtual environment
echo "Activating the virtual environment..."
source venv/bin/activate
if [[ "$VIRTUAL_ENV" != "" ]]; then
    echo "Virtual environment activated: $VIRTUAL_ENV"
else
    echo "Failed to activate virtual environment."
    exit 1
fi

# 3. Upgrade pip to the latest version
pip install --upgrade pip

# 4. Install dependencies
pip install -r requirements.txt

# 5. Create a blank .streamlit/secrets.toml.example file
mkdir -p .streamlit
touch .streamlit/secrets.toml.example

echo "Setup complete! Don't forget to re-activate your venv via the command `source venv/bin/activate` and add your secrets to the .secrets.toml file."