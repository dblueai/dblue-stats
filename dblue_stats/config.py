import os

from decouple import config

LOG_LEVEL = config("LOG_LEVEL", default="INFO")

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
