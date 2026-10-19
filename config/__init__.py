"""
Configuration module for the healthcare pipeline.
"""
import yaml
from pathlib import Path
from typing import Any, Dict, Optional


class Config:
    """Configuration manager for the pipeline."""
    
    _instance = None
    _config = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._config:
            self.load_config()
    
    def load_config(self, config_path: Optional[Path] = None):
        """Load configuration from YAML file."""
        if config_path is None:
            config_path = Path(__file__).resolve().parent.parent / "config" / "analysis.yml"
        
        with open(config_path, 'r') as f:
            self._config = yaml.safe_load(f)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a config value using dot notation (e.g., 'analysis.target_state')."""
        keys = key.split('.')
        value = self._config
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default
        return value if value is not None else default
    
    @property
    def target_state(self) -> str:
        return self.get('analysis.target_state', 'CT')
    
    @property
    def target_county(self) -> Optional[str]:
        return self.get('analysis.target_county')
    
    @property
    def target_specialty(self) -> Optional[str]:
        return self.get('analysis.target_specialty')
    
    @property
    def target_plan_year(self) -> int:
        return self.get('analysis.target_plan_year', 2024)
    
    @property
    def specialties(self) -> Dict[str, list]:
        return self.get('analysis.specialties', {})
    
    @property
    def provider_filters(self) -> Dict:
        return self.get('analysis.provider_filters', {})
    
    @property
    def population_config(self) -> Dict:
        return self.get('analysis.population', {})
    
    @property
    def snapshot_date(self) -> str:
        return self.get('analysis.snapshot_date', '2026-10-07')
    
    @property
    def chart_defaults(self) -> Dict:
        return self.get('analysis.chart_defaults', {})
    
    def get_specialty_list(self, group: str) -> list:
        """Get list of taxonomy descriptions for a specialty group."""
        return self.specialties.get(group, [])


# Global config instance
config = Config()