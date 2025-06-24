# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

### Development Setup
```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install watchdog  # Missing from requirements.txt but needed

# Run the application
python main.py
```

### Common Development Tasks
```bash
# Run the automation tool
python main.py

# Check Python syntax (no formal linter configured)
python -m py_compile main.py
python -m py_compile automation/*.py
python -m py_compile automation/actions/*.py
```

## Architecture Overview

This is a macOS automation tool that simulates human-like computer interactions. The core architecture consists of:

### Main Components

1. **MacAutomation Class** (`main.py:21-1021`): The central controller that:
   - Manages global hotkeys (Ctrl+Option+S/X/P/T)
   - Orchestrates automation workflows for Chrome and VSCode
   - Implements human-like mouse movements and typing
   - Monitors Hubstaff application files for changes

2. **Configuration System** (`automation/config.py`): Centralized settings management with:
   - Timing configurations for various actions
   - Safety features (fail-safe position, pause intervals)
   - Mouse movement and typing behavior parameters
   - File monitoring paths

3. **Threading Model**: 
   - Main thread handles keyboard listeners
   - Daemon threads execute automation workflows
   - File monitoring runs in a separate thread using watchdog

### Key Design Patterns

1. **Human-Like Behavior Simulation**:
   - Mouse movements use Bézier curves with random control points
   - Typing includes random delays, occasional errors, and corrections
   - Actions have configurable random pauses between them

2. **Application-Specific Workflows**:
   - Chrome: URL navigation, search, bookmarks, history browsing
   - VSCode: File operations, terminal commands, editor management
   - Each workflow randomly selects actions to appear natural

3. **macOS Integration**:
   - Uses pyobjc for native macOS API access
   - Leverages NSWorkspace for application state detection
   - AppleScript integration for reliable app switching

### Important Implementation Details

- **Application Focus**: Always verifies app focus before actions using `is_app_active()`
- **Coordinate System**: Uses pyautogui for screen coordinates and mouse control
- **Clipboard Operations**: Managed through pyperclip for text operations
- **XML Parsing**: Includes capability to parse Hubstaff organization data

### Current State Notes

- The `automation/actions/browser.py` and `automation/actions/vscode.py` files were recently deleted, with their functionality now integrated into `main.py`
- No formal testing framework is set up
- No linting or type checking configuration exists
- The watchdog dependency is missing from requirements.txt