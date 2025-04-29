from typing import Dict, Any

class BaseAction:
    """Base class for automation actions."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config

    def validate_config(self) -> bool:
        """Validate configuration for the action."""
        return True
