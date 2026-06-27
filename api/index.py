import os
import sys

# Add parent directory to sys.path to import modules from the project root
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
