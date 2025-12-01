import sys
import os

# Add the 'src' directory to sys.path so that pytest can find the modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))
