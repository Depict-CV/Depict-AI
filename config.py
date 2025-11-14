import os

import yaml
from dotenv import load_dotenv

load_dotenv()


class Config:
    API_URL = os.getenv("API_URL")

    base_dir = os.path.dirname(__file__)
    yaml_path = os.path.join(base_dir, "config.yaml")
    with open(yaml_path) as f:
        yaml_config = yaml.safe_load(f)

    annotation = yaml_config.get("annotation", {})


config = Config()
