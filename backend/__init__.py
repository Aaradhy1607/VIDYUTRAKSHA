"""
VIDYUTRAKSHA Backend Package Initialization
Ensures project root is added to sys.path regardless of execution directory.
"""
import sys
from pathlib import Path

# Add project root and backend dir to sys.path
_project_root = Path(__file__).resolve().parent.parent
_backend_dir = Path(__file__).resolve().parent

if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

if str(_backend_dir) not in sys.path:
    sys.path.insert(0, str(_backend_dir))
