import logging.config
import os

import yaml

from dblue_stats.config import LOG_LEVEL, PROJECT_ROOT

logger_config_file_path = os.path.join(PROJECT_ROOT, "configs", "logger.yaml")

with open(logger_config_file_path) as f:
    logging_config = yaml.safe_load(f.read())
    logging.config.dictConfig(logging_config)

logger = logging.getLogger('dblue_stats')
logger.setLevel(level=LOG_LEVEL)
