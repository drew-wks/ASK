## Setup
Before running any code or tests, run the following:

pip install -r requirements.txt
pip install -r requirements-dev.txt

If you are in the workspace you may need to address this as:
pip install -r /workspace/ASK/requirements-dev.txt


## CODEX Dev Environment Tips
Do NOT attempt to run any command which requires open network communication.  Your Dev environment has no network access and is sandboxed. No harm will come from trying but you will waste your effort.


Do NOT Run `install.sh` this script, if it exists. This script will be executed during environement setup for you during your environment setup prior to you arriving.  If you make changes that require new dependencies or services (like postgres etc...) to be installed, you must edit this file to include the dependencies and/or service installation and startup.

The 'install.sh' references dependencies gathered here: `requirements.txt` and `requirements-dev.txt`. 

Note that the effects will not take place until the next task session. 

ui.py is the "entrypoint file" for Streamlit. When this app runs on Streamlit Community Cloud, the working directory is always the root of this project. Streamlit requires paths to have forward slashesd to work in Streamlit Community Cloud.

## Testing

# Run pyright 
After editing a function
Before submitting a PR
Before running tests

# Run st.testing.v1.AppTest
After editing ui.py or any files in the pages directory
After I ask you to test the Streamlit app

# Network access
Whenever requests are blocked due to network access restrictions, create a report called requests that contains all the request and include it in yout PR

