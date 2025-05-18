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
            'min': 60,  # Increased minimum focus time
            'max': 180  # Increased maximum focus time
        }
    },
    'mouse': {
        'movement_duration': {
            'min': 0.4,
            'max': 1.2
        },
        'wiggle_range': {
            'min': -10,
            'max': 10
        }
    },
    'typing': {
        'error_probability': 0.05,
        'correction_delay': {
            'min': 0.1,
            'max': 0.5
        }
    },
    'scrolling': {
        'amount': {
            'min': 20,
            'max': 100
        },
        'pause_probability': 0.3
    },
    'development': {
        'local_urls': [
            'http://localhost:3000',
            'http://localhost:8000',
            'http://127.0.0.1:8000',
            'http://localhost:5000',
            'http://localhost:4200'
        ],
        'file_extensions': ['.py', '.js', '.html', '.css', '.json', '.md'],
        'common_commands': [
            'git status',
            'python manage.py runserver',
            'npm start',
            'ls -la',
            'docker ps',
            'npm run dev'
        ]
    }
}
