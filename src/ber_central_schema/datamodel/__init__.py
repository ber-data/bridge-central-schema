"""Data model package for ber-central-schema."""

from pathlib import Path
from .ber_central_schema import *  # noqa: F403

THIS_PATH = Path(__file__).parent

SCHEMA_DIRECTORY = THIS_PATH.parent / "schema"
MAIN_SCHEMA_PATH = SCHEMA_DIRECTORY / "ber_central_schema.yaml"
