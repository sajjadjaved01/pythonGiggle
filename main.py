import pyautogui
import pyperclip
import time
from typing import Tuple, Optional, Dict, Any, List, Callable
import random
import threading
from pynput import keyboard
from AppKit import NSWorkspace  # added macOS API for active app detection
import subprocess
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import tkinter as tk
from tkinter import ttk
import xml.etree.ElementTree as ET

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

        # Parse the XML file
        orgPath = self.config['monitor_path']['base_path'] + '/data/hubstaff.com/f8fb64d046ca609d94cdc23ecfdf83bb07647126/Organization.xml'
        organization_data = self.parse_organization_xml(orgPath)
        
        # Text to be typed, will be updated by user
        self.text_to_type = ""
        
        # File monitoring setup
        self.observer = None
        self.file_monitor_running = False

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

    @staticmethod
    def parse_organization_xml(file_path):
        """Parse the Organization.xml file and extract organization details.

        Args:
            file_path (str): Path to the XML file.

        Returns:
            dict: Extracted organization data.
        """
        tree = ET.parse(file_path)
        root = tree.getroot()

        # Extract organization details
        organization = root.find(".//item")
        metadata = organization.find("metadata")

        data = {
            "Organization ID": organization.find("organization_id").text,
            "Name": organization.find("name").text,
            "Screen Frequency": metadata.find("screen_frequency").text,
            "Idle Timeout": metadata.find("idle_timeout").text,
            "Screen Blur": metadata.find("screen_blur").text,
            "App Tracking": metadata.find("app_tracking").text,
            "Keep Idle": metadata.find("keep_idle").text,
            "Location Tracking": metadata.find("location_tracking").text,
            "Clients Allowed": metadata.find("clients_allowed").text,
            "Work Session Gap (Hours)": metadata.find(".//time_duration_hours").text,
            "Time Zone": metadata.find("time_zone").text,
            "Start Week On": metadata.find("start_week_on").text,
            "Color": metadata.find("color").text,
            "Monitor Background Processes": metadata.find("monitor_background_processes").text,
        }
        return data

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

    def setup_global_hotkeys(self) -> None:
        """Set up global keyboard shortcuts for controlling automation.

        Hotkeys:
        - Ctrl+Option+S: Start automation workflow
        - Ctrl+Option+X: Stop running automation
        - Ctrl+Option+P: Pause/resume automation
        - Ctrl+Option+T: Set text to type
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
        self.text_keys = {keyboard.Key.ctrl,
                          keyboard.Key.alt, keyboard.KeyCode.from_char('t')}

        # Track currently pressed keys
        self.current_keys = set()

        # Start keyboard listener in a daemon thread
        self._start_keyboard_listener()

        print("Global hotkeys enabled:")
        print("  Ctrl+Option+S: Start automation")
        print("  Ctrl+Option+X: Stop automation")
        print("  Ctrl+Option+P: Pause/Resume automation")
        print("  Ctrl+Option+T: Set text to type")

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
            # Wait 3 seconds before starting workflow
            time.sleep(3)
            # Start in a new thread to keep hotkeys responsive
            threading.Thread(target=self.run_focused_workflow,
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
            
        # Check for text input combination
        elif self.text_keys.issubset(self.current_keys):
            self.set_text_to_type()

    def _on_key_release(self, key) -> None:
        """Handle key release events."""
        try:
            self.current_keys.remove(key)
        except KeyError:
            # Key wasn't in the set
            pass
            
    def set_text_to_type(self) -> None:
        """Prompt user to input text that will be typed by the automation."""
        try:
            print("\nEnter text to be typed (press Enter when done):")
            # Use subprocess to run the osascript command for user input
            result = subprocess.run(
                ['osascript', '-e', 'text returned of (display dialog "Enter text to be typed:" default answer "" with title "Text Input")'],
                capture_output=True, text=True, check=True
            )
            self.text_to_type = result.stdout.strip()
            print(f"Text set: {self.text_to_type[:30]}{'...' if len(self.text_to_type) > 30 else ''}")
        except Exception as e:
            print(f"Error getting text input: {e}")
            
    def random_mouse_wiggle(self) -> None:
        """Slightly move mouse in random direction to simulate human hand movement."""
        current_x, current_y = pyautogui.position()
        offset_x = random.randint(-10, 10)
        offset_y = random.randint(-10, 10)
        self.natural_mouse_movement(current_x + offset_x, current_y + offset_y)
        
    def run_focused_workflow(self) -> None:
        """Run a focused workflow with mouse movement and keyboard typing until stopped."""
        print("Running focused workflow. Press Ctrl+Option+T to set text to type.")
        print("Starting file monitoring for " + self.config['monitor_path']['base_path'])

        # Start file monitoring
        self.start_file_monitoring()
        
        while self.running:
            try:
                while self.paused and self.running:
                    time.sleep(0.5)

                if not self.running:
                    break

                # Determine if we should move the mouse (20-40% of the time)
                if random.random() < 0.4:  # 40% maximum probability for mouse movement
                    self.perform_mouse_action()
                
                # Otherwise, perform a keyboard action if text is available
                elif self.text_to_type:
                    # Type a portion of the text
                    portion_size = random.randint(5, min(20, len(self.text_to_type)))
                    if portion_size > 0:
                        text_portion = self.text_to_type[:portion_size]
                        self.natural_typing(text_portion)
                        # Remove the typed portion from the text
                        self.text_to_type = self.text_to_type[portion_size:]
                        print(f"Typed: {text_portion}")
                
                # Random pause between actions
                time.sleep(random.uniform(0.5, 2.0))

            except pyautogui.FailSafeException:
                print("Failsafe triggered - mouse moved to corner")
                self.running = False
                break
            except Exception as e:
                print(f"Error occurred: {e}")
                time.sleep(1)
                continue

        # Stop file monitoring when workflow ends
        self.stop_file_monitoring()
        print("Workflow stopped")
        
    def perform_mouse_action(self) -> None:
        """Perform a random mouse action."""
        # Get screen dimensions
        screen_width, screen_height = pyautogui.size()
        
        # Choose a random action
        action = random.choice([
            "move", "move", "move",  # Higher weight for simple movement
            "click", "click",        # Medium weight for clicks
            "scroll", "wiggle"       # Lower weight for other actions
        ])
        
        try:
            if action == "move":
                # Move to random position on screen
                x = random.randint(100, screen_width - 100)
                y = random.randint(100, screen_height - 100)
                self.natural_mouse_movement(x, y)
                print(f"Mouse moved to {x}, {y}")
                
            elif action == "click":
                # Click at current or random position
                if random.random() < 0.5:  # 50% chance to click at current position
                    x, y = pyautogui.position()
                else:
                    x = random.randint(100, screen_width - 100)
                    y = random.randint(100, screen_height - 100)
                    self.natural_mouse_movement(x, y)
                    time.sleep(random.uniform(0.1, 0.3))
                pyautogui.click(x, y)
                print(f"Clicked at {x}, {y}")
                
            elif action == "scroll":
                # Scroll up or down
                direction = random.choice(["up", "down"])
                amount = random.randint(1, 5)
                self.scroll_page(direction, amount)
                print(f"Scrolled {direction} {amount} times")
                
            elif action == "wiggle":
                # Small random movement
                self.random_mouse_wiggle()
                print("Mouse wiggled")
        
        except Exception as e:
            print(f"Error in mouse action: {e}")
            
    class FileChangeHandler(FileSystemEventHandler):
        """Handler for file system changes."""
        
        def __init__(self, callback):
            self.callback = callback
            super().__init__()
            
        def on_any_event(self, event):
            """Called when a file system event occurs."""
            if event.is_directory:
                return
            self.callback(event)
            
    def handle_file_change(self, event) -> None:
        """Handle file change events in the specified format [status] (filename)."""
        event_type = event.event_type
        path = event.src_path
        filename = os.path.basename(path)
        
        # Map event_type to status
        status_map = {
            'created': 'created',
            'deleted': 'deleted',
            'modified': 'changed',
            'moved': 'moved'
        }
        status = status_map.get(event_type, event_type)
        
        # Print in the requested format
        print(f"[{status}] ({filename})")
    
    def start_file_monitoring(self) -> None:
        """Start monitoring for file changes."""
        if self.observer is None:
            try:
                # Expand the path
                monitor_path = os.path.expanduser(self.config['monitor_path']['base_path'])

                # Create event handler and observer
                event_handler = self.FileChangeHandler(self.handle_file_change)
                self.observer = Observer()
                self.observer.schedule(event_handler, monitor_path, recursive=True)
                self.observer.start()
                self.file_monitor_running = True
                print(f"File monitoring started for: {monitor_path}")
            except Exception as e:
                print(f"Error starting file monitoring: {e}")
        
    def stop_file_monitoring(self) -> None:
        """Stop file monitoring."""
        if self.observer is not None and self.file_monitor_running:
            try:
                self.observer.stop()
                self.observer.join()
                self.observer = None
                self.file_monitor_running = False
                print("File monitoring stopped")
            except Exception as e:
                print(f"Error stopping file monitoring: {e}")


# Example usage with global hotkeys
if __name__ == "__main__":
    print("Setting up Mac Automation with global hotkeys...")
    auto = MacAutomation()
    auto.setup_global_hotkeys()
    print("Ready! Use Ctrl+Alt+S to start the automation.")
    print("Use Ctrl+Alt+T to set text that will be typed.")
    print("The automation will monitor ~/Library/Application Support for file changes.")

    # Keep the main thread running to listen for hotkeys
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nExiting...")
