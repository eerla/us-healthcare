"""
Configuration loader for US Healthcare Data Pipeline.

Loads YAML config files and provides access to source registry,
geography settings, and analysis parameters.
"""

import yaml
from pathlib import Path


CONFIG_DIR = Path(__file__).resolve().parent


def load_config(name: str) -> dict:
    """Load a YAML config file by name (without .yml extension)."""
    path = CONFIG_DIR / f"{name}.yml"
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {path}")
    with open(path, "r") as f:
        return yaml.safe_load(f)


def get_sources() -> dict:
    """Return the source registry."""
    return load_config("sources")


def get_geography() -> dict:
    """Return geography settings."""
    return load_config("geography")


def get_analysis() -> dict:
    """Return analysis parameters."""
    return load_config("analysis")


def get_target_state() -> str:
    """Return the target state code from analysis config."""
    return get_analysis().get("target_state", "CT")


def get_snapshot_date() -> str:
    """Return the snapshot date from analysis config."""
    return get_analysis().get("snapshot_date", "2026-10-07")