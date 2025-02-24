import logging
import os

def setup_logging(config_file):
    enable_logging = get_config_value(config_file, 'loggingEnabled')
    if enable_logging == 'True':
        log_file = os.path.join(os.path.dirname(__file__), get_config_value(config_file, 'logFile'))

        # Ensure the logs directory exists
        os.makedirs(os.path.dirname(log_file), exist_ok=True)

        # Configure logging to both file and console
        logging.basicConfig(level=logging.INFO, format='%(asctime)s\t%(message)s', handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ])
        return print("Logging enabled . . .\n")
    else:
        return print("Logging disabled . . .\n")

def get_config_value(config_file, variable_name):
    with open(config_file, 'r') as f:
        config_data = f.read()
    for line in config_data.splitlines():
        if line.startswith(variable_name):
            return line.split('=')[1].strip()
    return None