import os
from pathlib import Path

from config.config_reader import ConfigReader


class BaseConfig:
    BASE_DIR = Path(__file__).resolve().parent.parent
    SCREENSHOT_DIR = BASE_DIR /"reports"/"screenshots"
    LOGS_DIR = BASE_DIR /"logs"
    ENVIRONMENT_DIR = BASE_DIR /"config"/"environment"
    REPORTS_DIR = BASE_DIR /"reports"/"all_reports"
    RECORD_VIDEOS_DIR = BASE_DIR /"reports"/"videos"

    ENVIRONMENT = ConfigReader.get_env_value("ENV","prod")
    HEADLESS = ConfigReader.get_bool("HEADLESS", "Ture")
    BROWSER = ConfigReader.get_env_value("BROWSER", "chromium")