"""Headless Streamlit status check for CI (no Streamlit dependency)."""

from __future__ import annotations

import logging
import os
import time
from pathlib import Path
from typing import Iterable, List

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

try:  # Python 3.11+
    import tomllib as tomli  # type: ignore[assignment]
except Exception:  # pragma: no cover - runner is 3.11/3.12 in Actions
    import tomli  # type: ignore[no-redef]


def _load_settings() -> tuple[str, List[str], List[str]]:
    """Load settings from ``.streamlit/secrets.toml`` or environment.

    Returns:
        Tuple of ``(url, success_strings, failure_strings)``.
    """
    default_url = "https://uscg-auxiliary-ask.streamlit.app/"
    default_success = ["Hosted with Streamlit"]
    default_failure = ["Zzzz"]

    url = os.environ.get("APP_URL", "")
    success = default_success
    failure = default_failure

    secrets_path = Path(".streamlit/secrets.toml")
    if secrets_path.exists():
        try:
            data = tomli.loads(secrets_path.read_text())
            url = str(data.get("APP_URL", url or default_url))
            success = list(data.get("SUCCESS_STRINGS", success))
            failure = list(data.get("FAILURE_STRINGS", failure))
        except Exception as exc:  # keep running with defaults
            logging.warning("Failed to parse secrets.toml: %s", exc)

    if not url:
        url = default_url

    return url, success, failure


def check_app_status(
    url: str,
    success_strings: Iterable[str] | None = None,
    failure_strings: Iterable[str] | None = None,
) -> None:
    """Open ``url`` headlessly and report health based on page text."""
    if success_strings is None:
        success_strings = ["Hosted with Streamlit"]
    if failure_strings is None:
        failure_strings = ["Zzzz"]

    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    driver = None
    try:
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")

        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()), options=chrome_options
        )

        driver.get(url)
        time.sleep(5)
        page_text = driver.find_element(By.TAG_NAME, "body").text

        for s in success_strings:
            if s and s in page_text:
                logging.info("App is working: %r", s)
                return

        for f in failure_strings:
            if f and f in page_text:
                logging.warning("App appears down: %r", f)
                return

        logging.info("App reachable but no indicator strings matched.")

    except Exception as exc:
        logging.error("Error accessing %s: %s", url, exc)
    finally:
        if driver is not None:
            driver.quit()


if __name__ == "__main__":
    target_url, ok_strings, bad_strings = _load_settings()
    check_app_status(target_url, ok_strings, bad_strings)
