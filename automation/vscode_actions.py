"""VSCode-specific automation actions and workflows."""

import time
import random
from typing import Optional, List, Tuple
import pyautogui
import pyperclip
from automation.mouse import NaturalMouseController
from automation.gestures import GestureController


class VSCodeAutomation:
    """Advanced VSCode automation with IDE-specific actions."""
    
    def __init__(self, config: dict = None):
        """Initialize VSCode automation with configuration."""
        self.config = config or {}
        self.mouse = NaturalMouseController(config)
        self.gestures = GestureController(config)
        
        # IntelliSense timing
        self.intellisense_wait = self.config.get('intellisense_wait', 0.5)
        self.suggestion_nav_delay = self.config.get('suggestion_nav_delay', 0.2)
    
    # Core Navigation Actions
    def go_to_definition(self) -> None:
        """Navigate to definition of symbol under cursor (F12)."""
        pyautogui.press('f12')
        time.sleep(0.5)  # Wait for navigation
    
    def go_to_implementation(self) -> None:
        """Navigate to implementation (Cmd+F12)."""
        pyautogui.hotkey('command', 'f12')
        time.sleep(0.5)
    
    def find_all_references(self) -> None:
        """Find all references to symbol (Shift+F12)."""
        pyautogui.hotkey('shift', 'f12')
        time.sleep(0.8)  # References panel takes time to load
    
    def peek_definition(self) -> None:
        """Peek at definition without navigating (Option+F12)."""
        pyautogui.hotkey('option', 'f12')
        time.sleep(0.5)
    
    def rename_symbol(self) -> None:
        """Start rename refactoring (F2)."""
        pyautogui.press('f2')
        time.sleep(0.3)
    
    def quick_fix(self) -> None:
        """Show quick fixes and refactorings (Cmd+.)."""
        pyautogui.hotkey('command', '.')
        time.sleep(self.intellisense_wait)
    
    def trigger_suggest(self) -> None:
        """Trigger IntelliSense suggestions (Ctrl+Space)."""
        pyautogui.hotkey('ctrl', 'space')
        time.sleep(self.intellisense_wait)
    
    def format_document(self) -> None:
        """Format entire document (Shift+Option+F)."""
        pyautogui.hotkey('shift', 'option', 'f')
        time.sleep(0.5)
    
    def format_selection(self) -> None:
        """Format selected code (Cmd+K Cmd+F)."""
        pyautogui.hotkey('command', 'k')
        time.sleep(0.1)
        pyautogui.hotkey('command', 'f')
    
    # Code Navigation Patterns
    def navigate_to_function(self, function_name: str) -> None:
        """Navigate to a specific function using symbol search.
        
        Args:
            function_name: Name of the function to find
        """
        # Open symbol search
        pyautogui.hotkey('command', 'shift', 'o')
        time.sleep(0.5)
        
        # Type function name with natural typing
        self._natural_type(function_name)
        time.sleep(0.5)
        
        # Select first result
        pyautogui.press('return')
        time.sleep(0.5)
    
    def explore_codebase(self, duration: int = 30) -> None:
        """Simulate natural codebase exploration.
        
        Args:
            duration: How long to explore in seconds
        """
        start_time = time.time()
        actions = [
            self._browse_files,
            self._read_code,
            self._follow_references,
            self._check_definition,
            self._scroll_and_read
        ]
        
        while time.time() - start_time < duration:
            action = random.choice(actions)
            action()
            time.sleep(random.uniform(1, 3))
    
    def _browse_files(self) -> None:
        """Browse through files in explorer."""
        # Open file explorer
        pyautogui.hotkey('command', 'shift', 'e')
        time.sleep(0.5)
        
        # Navigate with arrows
        for _ in range(random.randint(2, 5)):
            key = random.choice(['up', 'down'])
            pyautogui.press(key)
            time.sleep(random.uniform(0.2, 0.5))
        
        # Occasionally expand/collapse
        if random.random() < 0.3:
            pyautogui.press('right' if random.random() < 0.5 else 'left')
    
    def _read_code(self) -> None:
        """Simulate reading code with natural scrolling."""
        # Focus editor
        pyautogui.hotkey('command', '1')
        time.sleep(0.3)
        
        # Natural reading scroll
        self.gestures.natural_scroll_reading(lines=random.randint(5, 15))
    
    def _follow_references(self) -> None:
        """Follow code references naturally."""
        # Click on a random position in code
        x = random.randint(300, 800)
        y = random.randint(200, 600)
        self.mouse.natural_click(x, y)
        
        # Sometimes go to definition
        if random.random() < 0.5:
            self.go_to_definition()
    
    def _check_definition(self) -> None:
        """Check definition with peek."""
        self.peek_definition()
        time.sleep(random.uniform(1, 3))
        pyautogui.press('escape')  # Close peek
    
    def _scroll_and_read(self) -> None:
        """Scroll through code naturally."""
        direction = 'down' if random.random() < 0.7 else 'up'
        amount = random.randint(3, 10)
        
        for _ in range(amount):
            self.gestures.trackpad_scroll(0, 5 if direction == 'down' else -5, smooth=True)
            if random.random() < 0.2:  # Pause to "read"
                time.sleep(random.uniform(0.5, 2))
    
    # IntelliSense Interaction
    def interact_with_intellisense(self, accept_suggestion: bool = True) -> None:
        """Interact with IntelliSense suggestions.
        
        Args:
            accept_suggestion: Whether to accept a suggestion
        """
        self.trigger_suggest()
        
        # Navigate through suggestions
        nav_count = random.randint(0, 3)
        for _ in range(nav_count):
            pyautogui.press('down')
            time.sleep(self.suggestion_nav_delay)
        
        if accept_suggestion:
            pyautogui.press('tab')  # Accept with tab
        else:
            pyautogui.press('escape')  # Cancel
    
    def explore_method_signature(self) -> None:
        """Explore method signature with parameter hints."""
        # Type opening parenthesis to trigger parameter hints
        pyautogui.write('(')
        time.sleep(self.intellisense_wait)
        
        # Read parameter hints
        time.sleep(random.uniform(0.5, 1.5))
        
        # Close or continue
        if random.random() < 0.5:
            pyautogui.write(')')
        else:
            pyautogui.press('escape')
            pyautogui.press('backspace')
    
    def read_hover_documentation(self, x: int, y: int) -> None:
        """Hover over code to read documentation.
        
        Args:
            x: X coordinate to hover
            y: Y coordinate to hover
        """
        self.mouse.hover_and_wait(x, y, wait_time=random.uniform(1, 2))
    
    # Complex Workflows
    def debug_workflow(self, breakpoint_lines: List[int] = None) -> None:
        """Simulate debugging workflow.
        
        Args:
            breakpoint_lines: Line numbers for breakpoints
        """
        if breakpoint_lines is None:
            breakpoint_lines = [random.randint(10, 50) for _ in range(3)]
        
        # Set breakpoints
        for line in breakpoint_lines:
            pyautogui.hotkey('command', 'g')  # Go to line
            time.sleep(0.3)
            pyautogui.write(str(line))
            pyautogui.press('return')
            time.sleep(0.3)
            pyautogui.press('f9')  # Toggle breakpoint
            time.sleep(0.2)
        
        # Start debugging
        pyautogui.press('f5')
        time.sleep(2)
        
        # Step through code
        for _ in range(random.randint(3, 7)):
            action = random.choice(['f10', 'f11'])  # Step over or into
            pyautogui.press(action)
            time.sleep(random.uniform(1, 3))
            
            # Sometimes inspect variables
            if random.random() < 0.3:
                self._inspect_debug_variable()
    
    def _inspect_debug_variable(self) -> None:
        """Inspect variable during debugging."""
        # Hover over variable (simulated position)
        x = random.randint(300, 600)
        y = random.randint(200, 500)
        self.mouse.hover_and_wait(x, y, wait_time=1.5)
    
    def refactor_pattern(self, old_name: str, new_name: str) -> None:
        """Perform refactoring with find and replace.
        
        Args:
            old_name: Text to find
            new_name: Replacement text
        """
        # Open find and replace
        pyautogui.hotkey('command', 'shift', 'h')
        time.sleep(0.5)
        
        # Type search term
        self._natural_type(old_name)
        time.sleep(0.3)
        
        # Tab to replace field
        pyautogui.press('tab')
        time.sleep(0.2)
        
        # Type replacement
        self._natural_type(new_name)
        time.sleep(0.3)
        
        # Replace all (with confirmation)
        pyautogui.hotkey('command', 'option', 'return')
    
    def _natural_type(self, text: str) -> None:
        """Type text with natural delays and occasional corrections."""
        for char in text:
            # Occasional typo
            if random.random() < 0.05:
                wrong = random.choice('abcdefghijklmnopqrstuvwxyz')
                pyautogui.write(wrong)
                time.sleep(random.uniform(0.1, 0.3))
                pyautogui.press('backspace')
                time.sleep(random.uniform(0.1, 0.2))
            
            pyautogui.write(char)
            time.sleep(random.uniform(0.05, 0.15))
    
    # Git Integration
    def git_commit_workflow(self) -> None:
        """Simulate Git commit workflow in VSCode."""
        # Open source control
        pyautogui.hotkey('command', 'shift', 'g')
        time.sleep(0.5)
        
        # Stage changes (click on + icons)
        # This is simplified - in real use would need to detect UI elements
        for _ in range(random.randint(1, 3)):
            x = random.randint(50, 200)
            y = random.randint(200, 400)
            self.mouse.natural_click(x, y)
            time.sleep(0.5)
        
        # Click commit message box
        self.mouse.natural_click(150, 150)
        time.sleep(0.3)
        
        # Type commit message
        messages = [
            "Fix: Resolve null pointer issue",
            "Feature: Add new validation logic",
            "Refactor: Improve code readability",
            "Update: Enhance error handling"
        ]
        self._natural_type(random.choice(messages))
        
        # Commit (Cmd+Enter)
        time.sleep(0.5)
        pyautogui.hotkey('command', 'return')
    
    def navigate_between_errors(self) -> None:
        """Navigate between problems/errors in code."""
        # Go to next error
        pyautogui.press('f8')
        time.sleep(0.5)
        
        # Sometimes check the problem details
        if random.random() < 0.5:
            pyautogui.hotkey('command', 'shift', 'm')  # Show problems panel
            time.sleep(1)
            pyautogui.press('escape')  # Close panel