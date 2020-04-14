import os

from dblue_stats.config import PROJECT_ROOT

version_file = os.path.join(PROJECT_ROOT, "configs", "version.txt")

with open(version_file, 'r') as f:
    VERSION = f.read().strip()
