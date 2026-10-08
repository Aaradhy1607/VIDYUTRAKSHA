"""
VIDYUTRAKSHA - Structured Operational Logging
"""
import logging
import sys
from typing import Any, Dict


def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] [%(name)s] %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)]
    )
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)


logger = logging.getLogger("vidyutraksha")
