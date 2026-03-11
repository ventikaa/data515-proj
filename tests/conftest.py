"""Ensures that selenium opens chrome without GUI for Git Actions"""
import pytest
from selenium.webdriver.chrome.options import Options


@pytest.hookimpl
def pytest_setup_options():
    """Setting up pytest chrome on startup actions"""
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    return options
