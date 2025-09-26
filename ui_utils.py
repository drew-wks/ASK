import os  # needed for local testing
import datetime
import logging
from collections.abc import Mapping
from typing import List
import requests
import streamlit as st 
import pandas as pd
from pathlib import Path
from fnmatch import fnmatch
import re


parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Hide Streamlit's default UI elements: Main menu, footer, and header
COLLAPSED_CONTROL = """
    <style> 
        [data-testid="collapsedControl"] { display: none } html, body, [class*="st-"] {font-family: "Source Sans Pro", "Arial", "Helvetica", sans-serif !important;}
    </style>
    """

HIDE_STREAMLIT_UI = """
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
    </style>
    """

BLOCK_CONTAINER = """
        <style>
                .block-container {
                    padding-top: 1rem;
                    padding-bottom: 1rem;
                    padding-left: 3rem;
                    padding-right: 3rem;
                }
        </style>
        """

BLOCK_CONTAINER_2 = """
        <style>
                .block-container {
                    padding-top: 0rem;
                    padding-bottom: 1rem;
                    padding-left: 2rem;
                    padding-right: 2rem;
                }
        </style>
        """

FOOTER = """
    <style>
        .app-footer {
            bottom: 0;
            position: sticky;
            font-size: smaller;
            width: 700px;
            margin: auto;
            background: white;
            padding: 10px;
            border-top: 1px solid #ccc;
            text-align: left;
        }
    </style>
    <br><br>
    <div class="app-footer">
        <a href="Terms_of_service" target="_self">Terms of service</a>
    </div>
    """

LOGO = "https://raw.githubusercontent.com/drew-wks/ASK/main/images/ASK_logotype_color.png?raw=true"

logger = logging.getLogger(__name__)

_STATUS_COMPONENT_KEYWORDS = (
    "chat completions",
    "chatgpt api",
    "responses",
    "assistants",
    "agent",
    "gpts",
)


def apply_styles():
    st.markdown(COLLAPSED_CONTROL, unsafe_allow_html=True)
    st.markdown(HIDE_STREAMLIT_UI, unsafe_allow_html=True)
    st.markdown(BLOCK_CONTAINER_2, unsafe_allow_html=True)
    st.image(LOGO, use_container_width=True)


def _get_nested_string(data: Mapping[str, object], *path: str) -> str:
    """Return a string value from a nested mapping path."""

    current: object = data
    for key in path:
        if isinstance(current, Mapping):
            current = current.get(key)
            continue
        if hasattr(current, "get"):
            try:
                current = current.get(key)  # type: ignore[call-arg]
                continue
            except Exception:  # pragma: no cover - defensive
                return ""
        if hasattr(current, "__getitem__"):
            try:
                current = current[key]  # type: ignore[index]
                continue
            except Exception:  # pragma: no cover - defensive
                return ""
        return ""
    if current is None or isinstance(current, Mapping):
        return ""
    return str(current).strip()


def _resolve_chat_component_key() -> str:
    """Determine the chat component key for matching service status."""

    try:
        secrets_obj = st.secrets
        secrets_mapping: Mapping[str, object]
        if isinstance(secrets_obj, Mapping):
            secrets_mapping = secrets_obj
        else:
            secrets_mapping = dict(secrets_obj)  # type: ignore[arg-type]

        secret_paths = (
            ("RAG", "GENERATION", "generation_model"),
            ("RAG", "GENERATION", "langchain_chat_model"),
            ("ASK_generation_model",),
            ("generation_model",),
        )
        for path in secret_paths:
            value = _get_nested_string(secrets_mapping, *path)
            if value:
                return value.lower()
    except Exception:  # st.secrets raises if unset
        logger.debug("Unable to read OpenAI model from secrets", exc_info=True)

    env_vars = ("ASK_GENERATION_MODEL", "OPENAI_CHAT_MODEL", "OPENAI_MODEL")
    for env_key in env_vars:
        env_value = os.getenv(env_key, "").strip()
        if env_value:
            return env_value.lower()

    try:
        import rag  # type: ignore import-not-found

        config = getattr(rag, "CONFIG", None)
        if isinstance(config, Mapping):
            model = str(
                config.get("ASK_generation_model")
                or config.get("generation_model")
                or ""
            ).strip()
            if model:
                return model.lower()
    except Exception:
        logger.debug("Unable to infer OpenAI model from rag.CONFIG", exc_info=True)

    return ""


@st.cache_data
def get_openai_api_status() -> str:
    """Return availability summary for OpenAI chat endpoints.

    Returns:
        str: Human-readable summary describing OpenAI chat component availability.
    """

    components_url = "https://status.openai.com/api/v2/components.json"
    component_key = _resolve_chat_component_key()

    try:
        response = requests.get(components_url, timeout=10)
        response.raise_for_status()
        payload = response.json()
        components = payload.get("components", [])

        relevant_components: List[Mapping[str, object]] = []
        for component in components:
            if not isinstance(component, Mapping):
                continue
            name = str(component.get("name", "")).strip()
            if not name:
                continue
            normalized_name = name.lower()
            if any(keyword in normalized_name for keyword in _STATUS_COMPONENT_KEYWORDS) or (
                component_key and component_key in normalized_name
            ):
                relevant_components.append(component)

        if not relevant_components:
            logger.warning(
                "OpenAI status components missing for key '%s'",
                component_key or "unknown",
            )
            return "ChatGPT API component not found"

        degraded = [
            f"{component.get('name', 'Unknown')}: {component.get('status', 'unknown')}"
            for component in relevant_components
            if str(component.get("status", "")).strip().lower() != "operational"
        ]
        if degraded:
            return "OpenAI chat components degraded - " + "; ".join(degraded)

        component_names = ", ".join(
            str(component.get("name", "Unknown")) for component in relevant_components
        )
        return f"OpenAI chat components operational ({component_names})"

    except requests.exceptions.HTTPError as exc:
        return f"API check failed (HTTP error): {repr(exc)}"
    except requests.exceptions.Timeout:
        return "API check timed out"
    except requests.exceptions.RequestException as exc:
        return f"API check failed (Request error): {repr(exc)}"
    except Exception as exc:  # pylint: disable=broad-except
        return f"API check failed (Unknown error): {repr(exc)}"


def get_markdown(markdown_file):
    return Path(markdown_file).read_text()


@st.cache_data
def get_library_catalog_excel_and_date():
    """
    Retrieves the most recent Excel file matching the pattern 'docs_report_qdrant_cloud*.xlsx'
    from the 'docs/library_catalog/' directory. The function returns the file as a Pandas 
    DataFrame along with the timestamp from the filename in ISO 8601 format.

    Returns:
        tuple: (DataFrame, str) - The DataFrame containing the Excel file data and
        the timestamp from the filename as a string in the format 'YYYY-MM-DDTHH:MM:SSZ'.
        Returns (None, None) if no matching file is found or if an error occurs.
    """
    # defined here becuase function is accessed in several places. Use full path
    directory_path = './docs/library_catalog/'
    
    try:
        files_in_directory = os.listdir(directory_path)
    except FileNotFoundError:
        os.write(1, b"Directory not found.\n")
        return None, None

    # Use fnmatch for filename matching
    excel_files = [file for file in files_in_directory if fnmatch(file, "docs_report_qdrant_cloud*.xlsx")]
    if not excel_files:
        os.write(1, b"There is no matching Excel file in the directory.\n")
        return None, None

    # Function to extract the timestamp from a filename.
    def extract_timestamp(filename):
        # Expecting filename like: docs_report_qdrant_cloud_YYYY-MM-DDTHHMMSSZ.xlsx
        match = re.search(r'docs_report_qdrant_cloud_(\d{4}-\d{2}-\d{2}T\d{6}Z)\.xlsx', filename)
        if match:
            date_str = match.group(1)  # e.g., "2025-03-14T141504Z"
            try:
                dt = datetime.datetime.strptime(date_str, '%Y-%m-%dT%H%M%SZ')
                return dt
            except Exception:
                return None
        return None

    # Build a list of tuples (filename, extracted_timestamp) and filter out any that don't parse
    excel_files_with_time = []
    for file in excel_files:
        ts = extract_timestamp(file)
        if ts:
            excel_files_with_time.append((file, ts))
    
    if not excel_files_with_time:
        os.write(1, b"None of the Excel files have a valid timestamp in their filename.\n")
        return None, None

    # Sort files by the extracted timestamp, most recent first
    excel_files_with_time.sort(key=lambda x: x[1], reverse=True)
    most_recent_file, file_timestamp = excel_files_with_time[0]

    try:
        df = pd.read_excel(os.path.join(directory_path, most_recent_file))
    except Exception as e:
        os.write(1, f"Failed to read the Excel file: {e}\n".encode())
        return None, None

    # Format the timestamp from the filename to ISO 8601 (with colons)
    last_update_date = file_timestamp.strftime('%Y-%m-%dT%H:%M:%SZ')
    return df, last_update_date




def main():
    print("Running utils.py directly")
    # You can include test code for utility functions here, if desired

if __name__ == "__main__":
    main()
