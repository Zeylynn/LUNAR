import yaml
import os

conf_name = "sim-config.yaml"

def load_config():
    conf_dir = "../../config"
    base_dir = os.path.dirname(os.path.abspath(__file__))
    conf_dir = os.path.join(base_dir, conf_dir)
    conf_file = os.path.join(conf_dir, conf_name)

    with open(conf_file, "r", encoding="utf-8") as file:
        return yaml.safe_load(file)