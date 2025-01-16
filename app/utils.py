import json
import os
def load_settings():
    """Load settings from a configuration file (settings.json)"""
    settings_file = 'app/config.json'

    if not os.path.exists(settings_file):
        print(f"Settings file {settings_file} not found!")
        return None

    with open(settings_file, 'r') as f:
        settings = json.load(f)

    return settings
