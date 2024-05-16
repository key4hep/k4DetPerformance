import sys
import os

# Add the project root directory to the sys.path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

# Now you can import config
import config

# Access the baseDir from config.py

print(f"Base directory: {config.baseDir}")
