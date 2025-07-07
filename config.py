"""
Configuration Management
Environment detection and settings
"""

import os
from dataclasses import dataclass
from typing import List

@dataclass
class Config:
    """Application configuration"""
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = True
    mode: str = "mock"
    available_vendors: List[str] = None
    
    def __post_init__(self):
        """Auto-detect environment after initialization"""
        if self.available_vendors is None:
            self.available_vendors = []
        self._detect_environment()
    
    def _detect_environment(self) -> None:
        """Smart environment detection"""
        # Check for explicit mock mode
        if os.getenv('FORCE_MOCK', '').lower() in ('true', '1', 'yes'):
            self.mode = "mock"
            return
        
        # Check for vendor API keys
        vendor_checks = {
            'openai': 'OPENAI_API_KEY',
            'anthropic': 'ANTHROPIC_API_KEY', 
            'weaviate': 'WEAVIATE_API_KEY'
        }
        
        for vendor, env_var in vendor_checks.items():
            if os.getenv(env_var):
                self.available_vendors.append(vendor)
        
        # Set mode based on available vendors
        if self.available_vendors:
            self.mode = "hybrid"
        else:
            self.mode = "mock"
    
    @property
    def startup_time(self) -> str:
        """Expected startup time based on mode"""
        return "< 30 seconds" if self.mode == "mock" else "< 45 seconds"
    
    @property
    def demo_ready(self) -> bool:
        """Is the demo ready to run?"""
        return True  # Always ready with mock fallback

# Global config instance
_config = None

def get_config() -> Config:
    """Get or create global config instance"""
    global _config
    if _config is None:
        _config = Config()
    return _config