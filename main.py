import pyautogui
import pyperclip
import time
from typing import Tuple, Optional, Dict, Any, List, Callable
import random
import threading
from pynput import keyboard
from AppKit import NSWorkspace  # added macOS API for active app detection
import subprocess

from automation.config import DEFAULT_CONFIG


class MacAutomation:
    """Class to handle automated interactions with macOS applications."""

    def __init__(self, config: Dict[str, Any] = None):
        """Initialize automation with optional custom configuration."""
        # Merge custom config with defaults
        self.config = DEFAULT_CONFIG.copy()
        if config:
            self._merge_config(config)

        # Set safety parameters from config
        pyautogui.FAILSAFE = self.config['safety']['failsafe']
        pyautogui.PAUSE = self.config['safety']['pause']

    def _merge_config(self, custom_config: Dict[str, Any]) -> None:
        """Deep merge custom configuration with defaults."""
        def _merge_dicts(default: Dict, custom: Dict) -> Dict:
            for key, value in custom.items():
                if isinstance(value, dict) and key in default:
                    _merge_dicts(default[key], value)
                else:
                    default[key] = value
            return default

        _merge_dicts(self.config, custom_config)

    def move_mouse(self, x: int, y: int, duration: float = 0.5) -> None:
        """Move mouse to specified coordinates."""
        pyautogui.moveTo(x, y, duration=duration)

    def click_position(self, x: int, y: int) -> None:
        """Click at specified coordinates."""
        pyautogui.click(x, y)

    def type_text(self, text: str, interval: float = 0.1) -> None:
        """Type text with specified interval between keystrokes."""
        pyautogui.write(text, interval=interval)

    def _normalize_app_name(self, app_name: str) -> str:
        """Map friendly name to actual macOS application name for AppleScript."""
        mapping = {
            'chrome': 'Google Chrome',
            'google chrome': 'Google Chrome',
            'vscode': 'Visual Studio Code',
            'visual studio code': 'Visual Studio Code'
        }
        return mapping.get(app_name.lower(), app_name)

    def switch_to_app(self, app_name: str) -> None:
        """Bring application to front using AppleScript and confirm focus."""
        normalized = self._normalize_app_name(app_name)
        max_retries = self.config['safety']['max_retries']
        retry_delay = self.config['safety']['retry_delay']
        for attempt in range(max_retries):
            try:
                # Use AppleScript to activate the app
                subprocess.run(
                    ['osascript', '-e',
                        f'tell application "{normalized}" to activate'],
                    check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
                )
            except Exception:
                # fallback to Spotlight if AppleScript fails
                pyautogui.hotkey('command', 'space')
                time.sleep(self.config['timing']['app_switch_delay'])
                pyautogui.write(normalized)
                pyautogui.press('return')
            # allow time to switch
            time.sleep(self.config['timing']['app_switch_delay'] + 0.5)
            if self.verify_application_state(normalized):
                return
            time.sleep(retry_delay)
        raise RuntimeError(f"Unable to focus application: {normalized}")

    def verify_application_state(self, app_name: str) -> bool:
        """Verify that the expected application is currently in focus using macOS AppKit.

        Args:
            app_name (str): Name of the application to verify

        Returns:
            bool: True if frontmost application matches app_name
        """
        try:
            normalized = self._normalize_app_name(app_name)
            active_app = NSWorkspace.sharedWorkspace().frontmostApplication().localizedName()
            return normalized.lower() in active_app.lower()
        except Exception:
            return False

    def chrome_new_tab(self) -> None:
        """Open new tab in Chrome."""
        pyautogui.hotkey('command', 't')

    def chrome_navigate(self, url: str) -> None:
        """Navigate to URL in Chrome."""
        self.chrome_new_tab()
        pyautogui.hotkey('command', 'l')  # Focus address bar
        pyperclip.copy(url)  # Use clipboard for special characters
        pyautogui.hotkey('command', 'v')
        pyautogui.press('return')

    def chrome_google_search(self, query: str) -> None:
        """Perform a Google search.

        Args:
            query (str): Search query text
        """
        self.chrome_navigate('https://www.google.com')
        time.sleep(1.5)  # Wait for page load
        pyperclip.copy(query)
        pyautogui.hotkey('command', 'v')
        pyautogui.press('return')
        time.sleep(2)  # Wait for search results

    def chrome_stackoverflow_search(self, query: str) -> None:
        """Search Stack Overflow for a query.

        Args:
            query (str): Search query text
        """
        self.chrome_navigate('https://stackoverflow.com')
        time.sleep(2.0)  # Wait for page load
        # Find and click the search box
        pyautogui.hotkey('command', 'f')
        time.sleep(0.5)
        pyautogui.write('Search')
        time.sleep(0.5)
        pyautogui.press('escape')
        time.sleep(0.5)
        pyautogui.press('tab')  # Focus on search box
        pyperclip.copy(query)
        pyautogui.hotkey('command', 'v')
        pyautogui.press('return')
        time.sleep(2.5)  # Wait for search results

    def chrome_bookmark_page(self) -> None:
        """Bookmark the current page in Chrome."""
        pyautogui.hotkey('command', 'd')

    def chrome_open_bookmarks(self) -> None:
        """Open the bookmarks bar in Chrome."""
        pyautogui.hotkey('command', 'shift', 'b')

    def chrome_show_history(self) -> None:
        """Show browsing history in Chrome."""
        pyautogui.hotkey('command', 'y')

    def chrome_clear_history(self) -> None:
        """Clear browsing history in Chrome."""
        self.chrome_show_history()
        time.sleep(1)
        pyautogui.hotkey('command', 'a')  # Select all
        pyautogui.press('delete')
        time.sleep(1)

    def vscode_open_explorer(self) -> None:
        """Open the file explorer in VSCode."""
        pyautogui.hotkey('command', 'shift', 'e')

    def vscode_open_extension(self) -> None:
        """Open the extensions view in VSCode."""
        pyautogui.hotkey('command', 'shift', 'x')

    def vscode_toggle_sidebar(self) -> None:
        """Toggle the visibility of the sidebar in VSCode."""
        pyautogui.hotkey('command', 'b')

    def vscode_split_editor(self) -> None:
        """Split the editor into two panes in VSCode."""
        pyautogui.hotkey('command', '\\')

    def vscode_command_palette(self) -> None:
        """Open VSCode command palette."""
        pyautogui.hotkey('command', 'shift', 'p')

    def vscode_new_file(self) -> None:
        """Create new file in VSCode."""
        pyautogui.hotkey('command', 'n')

    def vscode_toggle_terminal(self) -> None:
        """Toggle integrated terminal in VSCode."""
        pyautogui.hotkey('command', '`')

    def vscode_search_files(self) -> None:
        """Open file search in VSCode."""
        pyautogui.hotkey('command', 'p')

    def minimize_window(self) -> None:
        """Minimize current window."""
        pyautogui.hotkey('command', 'm')

    def maximize_window(self) -> None:
        """Maximize current window."""
        pyautogui.click(pyautogui.size()[0] //
                        2, 10)  # Click top center of screen

    def switch_tab(self, direction: str = 'next') -> None:
        """Switch between tabs in the current application."""
        if direction == 'next':
            pyautogui.hotkey('command', 'shift', ']')
        else:
            pyautogui.hotkey('command', 'shift', '[')

    def scroll_page(self, direction: str = 'down', amount: int = 5) -> None:
        """Scroll the page up or down.

        Args:
            direction (str): 'up' or 'down'
            amount (int): number of scroll iterations
        """
        for _ in range(amount):
            if direction == 'down':
                pyautogui.scroll(-3)
            else:
                pyautogui.scroll(3)
            time.sleep(random.uniform(0.5, 1.5))

    def vscode_scroll_to_top(self) -> None:
        """Scroll to the top of a VSCode file."""
        pyautogui.hotkey('command', 'home')

    def vscode_scroll_to_bottom(self) -> None:
        """Scroll to the bottom of a VSCode file."""
        pyautogui.hotkey('command', 'end')

    def browser_refresh(self) -> None:
        """Refresh current browser page."""
        pyautogui.hotkey('command', 'r')

    def browser_back(self) -> None:
        """Go back one page in browser history."""
        pyautogui.hotkey('command', '[')

    def browser_forward(self) -> None:
        """Go forward one page in browser history."""
        pyautogui.hotkey('command', ']')

    def browser_close_tab(self) -> None:
        """Close current browser tab."""
        pyautogui.hotkey('command', 'w')

    def browser_reopen_tab(self) -> None:
        """Reopen last closed tab."""
        pyautogui.hotkey('command', 'shift', 't')

    def browser_zoom(self, action: str = 'in') -> None:
        """Zoom in or out in browser.

        Args:
            action (str): 'in' or 'out'
        """
        if action == 'in':
            pyautogui.hotkey('command', '+')
        else:
            pyautogui.hotkey('command', '-')

    def natural_mouse_movement(self, x: int, y: int, duration: Optional[float] = None) -> None:
        """Move mouse in a more human-like curve pattern.

        Args:
            x (int): Target x coordinate
            y (int): Target y coordinate
            duration (float, optional): Movement duration
        """
        # Random duration if not specified
        if duration is None:
            duration = random.uniform(0.4, 1.2)

        # Add slight randomness to target position
        x += random.randint(-5, 5)
        y += random.randint(-5, 5)

        # Move with random easing function
        pyautogui.moveTo(x, y, duration=duration,
                         tween=random.choice([
                             pyautogui.easeInQuad,
                             pyautogui.easeOutQuad,
                             pyautogui.easeInOutQuad
                         ]))

    def natural_typing(self, text: str, error_probability: float = 0.05) -> None:
        """Type text with human-like mistakes and corrections.

        Args:
            text (str): Text to type
            error_probability (float): Probability of making a typo
        """
        for char in text:
            # Randomly make typing mistakes
            if random.random() < error_probability:
                # Type wrong character
                wrong_char = random.choice(text.replace(char, ''))
                pyautogui.write(wrong_char, interval=random.uniform(0.1, 0.3))
                time.sleep(random.uniform(0.1, 0.5))
                # Delete wrong character
                pyautogui.press('backspace')
                time.sleep(random.uniform(0.1, 0.3))

            # Type correct character with random interval
            pyautogui.write(char, interval=random.uniform(0.05, 0.2))

            # Occasionally pause while typing
            if random.random() < 0.1:
                time.sleep(random.uniform(0.3, 1.0))

    def natural_scroll(self, direction: str = 'down', distance: int = 300) -> None:
        """Scroll with varying speeds and pauses.

        Args:
            direction (str): 'up' or 'down'
            distance (int): Total scroll distance
        """
        remaining = distance
        while remaining > 0:
            # Variable scroll amount
            amount = min(remaining, random.randint(20, 100))
            remaining -= amount

            # Variable scroll speed
            if direction == 'down':
                pyautogui.scroll(-amount)
            else:
                pyautogui.scroll(amount)

            # Random pause between scrolls
            if random.random() < 0.3:
                time.sleep(random.uniform(0.3, 1.5))

    def random_mouse_wiggle(self) -> None:
        """Slightly move mouse in random direction to simulate human hand movement."""
        current_x, current_y = pyautogui.position()
        offset_x = random.randint(-10, 10)
        offset_y = random.randint(-10, 10)
        self.natural_mouse_movement(current_x + offset_x, current_y + offset_y)

    def setup_global_hotkeys(self) -> None:
        """Set up global keyboard shortcuts for controlling automation.

        Hotkeys:
        - Ctrl+Option+S: Start automation workflow
        - Ctrl+Option+X: Stop running automation
        - Ctrl+Option+P: Pause/resume automation
        """
        self.running = False
        self.paused = False
        self.listener = None

        # Define hotkey combinations
        self.start_keys = {keyboard.Key.ctrl,
                           keyboard.Key.alt, keyboard.KeyCode.from_char('s')}
        self.stop_keys = {keyboard.Key.ctrl,
                          keyboard.Key.alt, keyboard.KeyCode.from_char('x')}
        self.pause_keys = {keyboard.Key.ctrl,
                           keyboard.Key.alt, keyboard.KeyCode.from_char('p')}

        # Track currently pressed keys
        self.current_keys = set()

        # Start keyboard listener in a daemon thread
        self._start_keyboard_listener()

        print("Global hotkeys enabled:")
        print("  Ctrl+Option+S: Start automation")
        print("  Ctrl+Option+X: Stop automation")
        print("  Ctrl+Option+P: Pause/Resume automation")

    def _start_keyboard_listener(self) -> None:
        """Start the keyboard listener in a daemon thread."""
        if self.listener is None or not self.listener.is_alive():
            self.listener = keyboard.Listener(
                on_press=self._on_key_press,
                on_release=self._on_key_release,
                daemon=True
            )
            self.listener.start()

    def _on_key_press(self, key) -> None:
        """Handle key press events and trigger hotkey actions."""
        self.current_keys.add(key)

        # Check for start combination
        if self.start_keys.issubset(self.current_keys) and not self.running:
            print("\nStarting automation workflow...")
            self.running = True
            # Wait 8 seconds before starting workflow
            time.sleep(8)
            # Start in a new thread to keep hotkeys responsive
            threading.Thread(target=self.run_workflow,
                             daemon=True).start()

        # Check for stop combination
        elif self.stop_keys.issubset(self.current_keys) and self.running:
            print("\nStopping automation...")
            self.running = False
            self.paused = False

        # Check for pause combination
        elif self.pause_keys.issubset(self.current_keys) and self.running:
            self.paused = not self.paused
            status = "Paused" if self.paused else "Resumed"
            print(f"\n{status} automation...")

    def _on_key_release(self, key) -> None:
        """Handle key release events."""
        try:
            self.current_keys.remove(key)
        except KeyError:
            # Key wasn't in the set
            pass

    def run_workflow(self) -> None:
        """Run macOS-compatible automated workflow until stopped."""
        # Setup logging
        workflow_log = self._setup_workflow_logging()

        search_queries = [
            'python best practices',
            'software design patterns',
            'git workflow examples',
            'coding best practices',
            'web development trends'
        ]

        # Get local development URLs from config
        local_urls = self.config['development']['local_urls']
        dev_commands = self.config['development']['common_commands']

        while self.running:
            try:
                while self.paused and self.running:
                    time.sleep(0.5)

                if not self.running:
                    break

                # Execute extended macOS-native tasks
                self.perform_random_tasks()

                # Natural pause between sequences
                time.sleep(random.uniform(60, 120))  # 1-2 minute breaks

            except pyautogui.FailSafeException:
                print("Failsafe triggered - mouse moved to corner")
                self.running = False
                break
            except Exception as e:
                print(f"Error occurred: {e}")
                continue

        print("Workflow stopped")

    def _setup_workflow_logging(self) -> Dict[str, Any]:
        """Set up logging for the workflow session.

        Returns:
            Dict[str, Any]: Log dictionary to track metrics
        """
        return {
            'start_time': time.time(),
            'actions': [],
            'app_time': {
                'vscode': 0,
                'chrome': 0,
                'other': 0
            },
            'errors': []
        }

    def _log_action(self, log: Dict[str, Any], action: str, app: str, success: bool,
                    error: Optional[str] = None) -> None:
        """Log an action to the workflow log.

        Args:
            log (Dict[str, Any]): Workflow log dictionary
            action (str): Action performed
            app (str): Application where action was performed
            success (bool): Whether action was successful
            error (Optional[str]): Error message if applicable
        """
        log['actions'].append({
            'timestamp': time.time(),
            'action': action,
            'app': app,
            'success': success,
            'error': error
        })

        if not success and error:
            log['errors'].append({
                'timestamp': time.time(),
                'action': action,
                'error': error
            })

    def _vscode_file_navigation(self) -> None:
        """Simulate file navigation in VSCode."""
        if not self.running:
            return
        self.vscode_search_files()
        time.sleep(random.uniform(1, 3))

        # Type different file types to search
        file_extensions = self.config['development']['file_extensions']
        for _ in range(random.randint(2, 4)):
            ext = random.choice(file_extensions)
            self.natural_typing(f"file{ext}")
            time.sleep(random.uniform(2, 5))
            pyautogui.press('escape')
            time.sleep(random.uniform(1, 3))

        # Open a file
        self.vscode_search_files()
        time.sleep(random.uniform(1, 2))
        self.natural_typing("main")
        time.sleep(random.uniform(0.5, 1))
        pyautogui.press('return')

        # Scroll and read through file
        self.natural_scroll('down', random.randint(400, 800))
        time.sleep(random.uniform(10, 20))

    def _vscode_terminal_work(self, commands: list) -> None:
        """Simulate terminal usage in VSCode."""
        if not self.running:
            return
        self.vscode_toggle_terminal()
        time.sleep(random.uniform(1, 3))

        # Execute 2-3 commands
        for _ in range(random.randint(2, 3)):
            command = random.choice(commands)
            self.natural_typing(command)
            time.sleep(random.uniform(0.5, 1))
            pyautogui.press('return')
            time.sleep(random.uniform(3, 8))

        # Sometimes clear terminal
        if random.random() > 0.7:
            self.natural_typing("clear")
            pyautogui.press('return')

        time.sleep(random.uniform(1, 3))
        # Toggle terminal off sometimes
        if random.random() > 0.5:
            self.vscode_toggle_terminal()

    def _vscode_coding_session(self) -> None:
        """Simulate actual coding activities."""
        if not self.running:
            return
        # Navigate between open files
        for _ in range(random.randint(2, 4)):
            self.switch_tab(random.choice(['next', 'previous']))
            time.sleep(random.uniform(2, 5))

        # Code navigation activities
        self.vscode_navigate_code()

        # Simulated typing code with pauses
        for _ in range(random.randint(1, 3)):
            # Type some code with natural typing
            self.natural_typing("def process_data(input_data):")
            pyautogui.press('return')
            self.natural_typing("    result = []")
            pyautogui.press('return')
            self.natural_typing("    for item in input_data:")
            pyautogui.press('return')
            time.sleep(random.uniform(3, 8))  # Think pause

        # simulate selecting a code snippet with mouse drag
        start_x, start_y = random.randint(300, 700), random.randint(200, 600)
        end_x, end_y = start_x + \
            random.randint(50, 150), start_y + random.randint(20, 100)
        self.natural_mouse_movement(start_x, start_y)
        pyautogui.mouseDown()
        self.natural_mouse_movement(end_x, end_y)
        pyautogui.mouseUp()
        time.sleep(random.uniform(0.5, 1.5))

        # occasionally save selection or bring up context menu
        if random.random() > 0.5:
            pyautogui.hotkey('command', 'c')  # copy

        # Save file occasionally
        if random.random() > 0.6:
            pyautogui.hotkey('command', 's')

        # Add more realistic coding patterns
        if random.random() > 0.6:
            self._simulate_debugging_session()

    def _simulate_debugging_session(self) -> None:
        """Simulate a debugging session in VSCode."""
        if not self.running:
            return
        # Set breakpoint
        pyautogui.press('f9')
        time.sleep(random.uniform(1, 2))

        # Start debugging
        pyautogui.hotkey('f5')
        time.sleep(random.uniform(3, 8))

        # Step through code
        for _ in range(random.randint(2, 5)):
            step_action = random.choice(
                ['f10', 'f11'])  # Step over or step into
            pyautogui.press(step_action)
            time.sleep(random.uniform(2, 5))

            # Inspect variables
            if random.random() > 0.7:
                self.natural_mouse_movement(
                    random.randint(100, 400),
                    random.randint(200, 500)
                )
                pyautogui.click()
                time.sleep(random.uniform(1, 3))

        # Stop debugging
        pyautogui.hotkey('shift', 'f5')
        time.sleep(random.uniform(1, 2))

    def _vscode_ui_interactions(self) -> None:
        """Simulate interactions with VSCode UI elements."""
        if not self.running:
            return
        ui_actions = [
            self.vscode_open_explorer,
            self.vscode_open_extension,
            self.vscode_toggle_sidebar,
            self.vscode_split_editor,
            self.vscode_command_palette
        ]
        for action in random.sample(ui_actions, random.randint(1, 3)):
            action()
            time.sleep(random.uniform(3, 8))
            # simulate clicking on a UI element (e.g. an explorer item or extension)
            x, y = random.randint(100, 700), random.randint(100, 500)
            self.natural_mouse_movement(x, y)
            pyautogui.click()
            time.sleep(random.uniform(1, 3))

    def vscode_navigate_code(self) -> None:
        """Navigate through code using VSCode's code navigation features."""
        navigation_actions = [
            (lambda: pyautogui.hotkey('command', 'f12'), "Go to Definition"),
            (lambda: pyautogui.hotkey('command', 'shift', 'o'), "Go to Symbol"),
            (lambda: pyautogui.hotkey('command', 'shift', 'r'), "Go to References"),
            (lambda: pyautogui.hotkey('alt', 'left'), "Go Back"),
            (lambda: pyautogui.hotkey('command', 'k', 'command', 'i'), "Show Hover")
        ]

        for action, name in random.sample(navigation_actions, random.randint(2, 4)):
            action()
            time.sleep(random.uniform(2, 5))

    def vscode_dev_tools(self) -> None:
        """Use various VSCode development tools."""
        dev_actions = [
            (lambda: pyautogui.hotkey('command', 'shift', 'f'), "Global Search"),
            (lambda: pyautogui.hotkey('command', '.'), "Quick Fix"),
            (lambda: pyautogui.hotkey('command', 'k',
             'command', 'f'), "Format Selection"),
            (lambda: pyautogui.hotkey('f8'), "Go to Next Problem"),
            (lambda: pyautogui.hotkey('command', 'shift', 'm'), "Show Problems Panel")
        ]

        for action, name in random.sample(dev_actions, random.randint(2, 4)):
            action()
            time.sleep(random.uniform(1.5, 4))

    def perform_random_tasks(self) -> None:
        """Execute a random sequence of tasks with macOS‐native app switching."""
        quick_task_sequences = [
            {
                'name': 'Quick Code Review',
                'actions': [
                    lambda: self.switch_to_app('Visual Studio Code'),
                    lambda: self.vscode_search_files(),
                    lambda: self.natural_typing('main.py'),
                    lambda: pyautogui.press('return'),
                    lambda: self.natural_scroll(
                        'down', random.randint(100, 200))
                ]
            },
            {
                'name': 'Quick Documentation Check',
                'actions': [
                    lambda: self.switch_to_app('Google Chrome'),
                    lambda: self.chrome_stackoverflow_search(
                        'python quick example'),
                    lambda: self.natural_scroll(
                        'down', random.randint(100, 200))
                ]
            },
            {
                'name': 'Quick Terminal Check',
                'actions': [
                    lambda: self.switch_to_app('Visual Studio Code'),
                    lambda: self.vscode_toggle_terminal(),
                    lambda: self.natural_typing('git status'),
                    lambda: pyautogui.press('return'),
                    lambda: time.sleep(random.uniform(1, 2))
                ]
            },
            {
                'name': 'Quick Debug Check',
                'actions': [
                    lambda: self.switch_to_app('Visual Studio Code'),
                    lambda: pyautogui.hotkey('command', 'shift', 'm'),
                    lambda: time.sleep(random.uniform(1, 2)),
                    lambda: pyautogui.press('escape')
                ]
            }
        ]

        # Select and execute 1-2 quick sequences for short duration
        selected_sequences = random.sample(
            quick_task_sequences, random.randint(1, 2))

        for sequence in selected_sequences:
            print(f"\nExecuting quick task: {sequence['name']}")
            for action in sequence['actions']:
                if not self.running or self.paused:
                    return
                try:
                    action()
                except Exception as e:
                    print(f"Error in {sequence['name']}: {e}")
                    continue
                # Shorter pauses between actions
                time.sleep(random.uniform(0.5, 1))

        task_sequences = [
            {
                'name': 'Documentation Research',
                'actions': [
                    lambda: self.switch_to_app('Google Chrome'),
                    lambda: self.chrome_navigate('https://github.com'),
                    lambda: self.natural_scroll(
                        'down', random.randint(200, 500)),
                    lambda: time.sleep(random.uniform(10, 20)),
                    lambda: self.chrome_navigate(
                        'https://github.com/sajjadjaved01'),
                    lambda: self.natural_scroll(
                        'down', random.randint(300, 600))
                ]
            },
            {
                'name': 'Code Review',
                'actions': [
                    lambda: self.switch_to_app('Visual Studio Code'),
                    lambda: self.vscode_open_explorer(),
                    lambda: time.sleep(random.uniform(3, 5)),
                    lambda: self.natural_typing('git diff'),
                    lambda: pyautogui.press('return'),
                    lambda: self.natural_scroll(
                        'down', random.randint(100, 300))
                ]
            },
            {
                'name': 'Bug Investigation',
                'actions': [
                    lambda: self.switch_to_app('Google Chrome'),
                    lambda: self.chrome_stackoverflow_search(
                        'python error handling best practices'),
                    lambda: time.sleep(random.uniform(5, 10)),
                    lambda: self.switch_to_app('Visual Studio Code'),
                    lambda: self._simulate_debugging_session()
                ]
            },
            {
                'name': 'API Testing',
                'actions': [
                    lambda: self.switch_to_app('Google Chrome'),
                    lambda: self.chrome_navigate('http://localhost:8000'),
                    lambda: time.sleep(random.uniform(3, 7)),
                    lambda: self.natural_scroll(
                        'down', random.randint(200, 400)),
                    lambda: self.browser_refresh()
                ]
            }
        ]

        # Randomly select and execute 2-3 unique task sequences
        selected_sequences = random.sample(
            task_sequences, random.randint(2, 3))

        for sequence in selected_sequences:
            print(f"\nExecuting task sequence: {sequence['name']}")
            for action in sequence['actions']:
                if not self.running or self.paused:
                    return
                try:
                    action()
                except Exception as e:
                    print(f"Error in {sequence['name']}: {e}")
                    continue

        extended_task_sequences = [
            {
                'name': 'Full Development Cycle',
                'actions': [
                    lambda: self.switch_to_app('Visual Studio Code'),
                    lambda: self._vscode_coding_session(),
                    lambda: time.sleep(random.uniform(180, 300)),  # 3-5 minutes coding
                    lambda: self.switch_to_app('Google Chrome'),
                    lambda: self.chrome_stackoverflow_search('laravel best practices with vite'),
                    lambda: time.sleep(random.uniform(120, 180)),  # 2-3 minutes reading
                    lambda: self.switch_to_app('Visual Studio Code'),
                    lambda: self._simulate_debugging_session(),
                    lambda: time.sleep(random.uniform(240, 360))   # 4-6 minutes debugging
                ]
            },
            {
                'name': 'Developer Intensive Workflow',
                'actions': [
                    lambda: self.switch_to_app('Visual Studio Code'),
                    lambda: self.vscode_search_files(),
                    lambda: time.sleep(1),
                    lambda: self.natural_mouse_movement(random.randint(300, 500), random.randint(200, 300)),
                    lambda: self.natural_typing('def new_function():'),
                    lambda: pyautogui.press('return'),
                    lambda: self.natural_typing('    pass'),
                    lambda: pyautogui.press('return'),
                    lambda: time.sleep(1),
                    lambda: self.natural_mouse_movement(random.randint(300, 500), random.randint(400, 600)),
                    lambda: self.click_position(random.randint(300, 500), random.randint(400, 600)),
                    lambda: self.switch_tab('next'),
                    lambda: time.sleep(3),
                    lambda: self.vscode_dev_tools(),
                    lambda: self.natural_mouse_wiggle(),
                    lambda: self.vscode_toggle_terminal(),
                    lambda: self.natural_typing('npm start'),
                    lambda: pyautogui.press('return'),
                    lambda: time.sleep(3),
                    lambda: self.switch_to_app('Google Chrome'),
                    lambda: self.natural_mouse_movement(random.randint(100, 300), random.randint(100, 300)),
                    lambda: self.chrome_google_search('latest vscode tips'),
                    lambda: self.browser_refresh(),
                    # Extended macOS-native work period (15–25 min)
                    lambda: time.sleep(random.uniform(900, 1500))
                ]
            }
        ]
        
        # Ensure macOS app focus after each extended task action
        selected_sequences = random.sample(extended_task_sequences, random.randint(1, 2))
        for sequence in selected_sequences:
            print(f"\nExecuting extended task: {sequence['name']}")
            for action in sequence['actions']:
                if not self.running or self.paused:
                    return
                try:
                    action()
                    # Verify macOS frontmost app after critical actions
                    if not self.verify_application_state('Visual Studio Code') and not self.verify_application_state('Google Chrome'):
                        raise RuntimeError("Application switch failed")
                    if random.random() > 0.7:
                        time.sleep(random.uniform(30, 60))
                except Exception as e:
                    print(f"Error in {sequence['name']}: {e}")
                    continue


# Example usage with global hotkeys
if __name__ == "__main__":
    print("Setting up Mac Automation with global hotkeys...")
    auto = MacAutomation()
    auto.setup_global_hotkeys()
    print("Ready! Use Ctrl+Alt+S to start the automation.")

    # Keep the main thread running to listen for hotkeys
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nExiting...")
