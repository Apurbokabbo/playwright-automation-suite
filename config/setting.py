import yaml
from config.base_config import BaseConfig



ENVIRONMENT = BaseConfig.ENVIRONMENT
HEADLESS = BaseConfig.HEADLESS
BROWSER = BaseConfig.BROWSER


try:
    yaml_path =BaseConfig.ENVIRONMENT_DIR/f"{ENVIRONMENT}.yaml"
    with open(yaml_path,"r") as file:
        config_data = yaml.safe_load(file)
        BASE_URL = config_data["base_url"]
except FileNotFoundError:
    print(f"No config file found at {BASE_URL}")
    BASE_URL= None
