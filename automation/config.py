from typing import Dict, Any

DEFAULT_CONFIG: Dict[str, Any] = {
    'safety': {
        'failsafe': True,
        'pause': 0.5,
        'max_retries': 3,
        'retry_delay': 1.0,
    },
    'timing': {
        'typing_interval': 0.1,
        'app_switch_delay': 1.0,
        'page_load_delay': 2.0,
        'action_delay': {
            'min': 0.3,
            'max': 1.5
        },
        'vscode_focus_time': {
            'min': 60,
            'max': 180
        }
    },
    # ... rest of the config ...
}
