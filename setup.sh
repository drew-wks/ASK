#!/bin/bash

# 1. Create virtual environment
python3 -m venv venv

# 2. Activate virtual environment
source venv/bin/activate

# 3. Upgrade pip to the latest version
pip install --upgrade pip

# 4. Install dependencies
pip install -r requirements.txt

# 5. Create a blank .streamlit/secrets.toml.example file
mkdir -p .streamlit
touch .streamlit/secrets.toml.example

echo "Setup complete! Don't forget to add your secrets to the .secrets.toml file."