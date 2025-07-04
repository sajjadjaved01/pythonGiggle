"""Trackpad gesture support for macOS automation."""

import time
import math
import random
from typing import Optional, Tuple
from Quartz import (
    CGEventCreateScrollWheelEvent,
    CGEventPost,
    kCGHIDEventTap,
    kCGScrollEventUnitLine,
    CGEventCreateMouseEvent,
    CGEventSetIntegerValueField,
    kCGMouseEventSubtype,
    CGPointMake,
    kCGEventLeftMouseDragged
)
import pyautogui


class GestureController:
    """Handle trackpad gestures for natural macOS interaction."""
    
    def __init__(self, config: dict = None):
        """Initialize gesture controller with optional configuration."""
        self.config = config or {}
        self.gesture_sensitivity = self.config.get('gesture_sensitivity', 1.0)
        self.gesture_duration = self.config.get('gesture_duration', 0.5)
    
    def trackpad_swipe(self, direction: str, fingers: int = 3, distance: int = 100) -> None:
        """Perform trackpad swipe gesture.
        
        Args:
            direction: 'left', 'right', 'up', or 'down'
            fingers: Number of fingers (2-4)
            distance: Swipe distance in pixels
        """
        if fingers not in [2, 3, 4]:
            raise ValueError("Swipe must use 2, 3, or 4 fingers")
        
        # Get current mouse position
        current_x, current_y = pyautogui.position()
        
        # Calculate end position based on direction
        directions = {
            'left': (-distance, 0),
            'right': (distance, 0),
            'up': (0, -distance),
            'down': (0, distance)
        }
        
        if direction not in directions:
            raise ValueError(f"Invalid direction: {direction}")
        
        dx, dy = directions[direction]
        end_x = current_x + dx
        end_y = current_y + dy
        
        # Perform swipe gesture
        steps = 20
        for i in range(steps + 1):
            progress = i / steps
            x = current_x + (dx * progress)
            y = current_y + (dy * progress)
            
            # Create swipe event
            event = CGEventCreateMouseEvent(
                None,
                kCGEventLeftMouseDragged,
                CGPointMake(x, y),
                0
            )
            
            # Set number of fingers
            CGEventSetIntegerValueField(event, kCGMouseEventSubtype, fingers)
            CGEventPost(kCGHIDEventTap, event)
            
            time.sleep(self.gesture_duration / steps)
    
    def trackpad_pinch(self, scale: float, duration: Optional[float] = None) -> None:
        """Perform pinch gesture for zoom using keyboard shortcuts.
        
        Args:
            scale: Scale factor (>1 for zoom in, <1 for zoom out)
            duration: Gesture duration in seconds
        """
        # Use keyboard shortcuts as alternative to gesture events
        if scale > 1:
            # Zoom in
            pyautogui.hotkey('command', '+')
        else:
            # Zoom out
            pyautogui.hotkey('command', '-')
        
        time.sleep(duration or self.gesture_duration)
    
    def trackpad_rotate(self, degrees: float, duration: Optional[float] = None) -> None:
        """Perform rotation gesture simulation.
        
        Args:
            degrees: Rotation angle (positive for clockwise)
            duration: Gesture duration in seconds
        """
        # Since rotation gestures are not directly available,
        # we'll simulate with mouse movements in a circular pattern
        duration = duration or self.gesture_duration
        current_x, current_y = pyautogui.position()
        radius = 50
        steps = 20
        
        for i in range(steps + 1):
            progress = i / steps
            angle = (degrees * progress) * (3.14159 / 180)  # Convert to radians
            
            # Calculate circular movement
            x = current_x + radius * math.cos(angle)
            y = current_y + radius * math.sin(angle)
            
            pyautogui.moveTo(x, y, duration=0)
            time.sleep(duration / steps)
    
    def trackpad_scroll(self, x: int, y: int, smooth: bool = True) -> None:
        """Perform smooth trackpad scrolling.
        
        Args:
            x: Horizontal scroll amount (positive = right)
            y: Vertical scroll amount (positive = down)
            smooth: Use smooth scrolling animation
        """
        if smooth:
            # Smooth scrolling with multiple small events
            steps = abs(max(x, y, key=abs)) // 3
            if steps == 0:
                steps = 1
                
            for i in range(steps):
                # Create scroll event
                event = CGEventCreateScrollWheelEvent(
                    None,
                    kCGScrollEventUnitLine,
                    2,  # wheelCount (2 for x and y)
                    int(y / steps),  # vertical
                    int(x / steps)   # horizontal
                )
                
                CGEventPost(kCGHIDEventTap, event)
                time.sleep(0.01)
        else:
            # Single scroll event
            event = CGEventCreateScrollWheelEvent(
                None,
                kCGScrollEventUnitLine,
                2,  # wheelCount
                y,  # vertical
                x   # horizontal
            )
            CGEventPost(kCGHIDEventTap, event)
    
    def vscode_gesture_navigation(self, action: str) -> None:
        """Perform VSCode-specific gesture navigation.
        
        Args:
            action: Navigation action to perform
                - 'next_tab': 3-finger swipe right
                - 'prev_tab': 3-finger swipe left
                - 'back': 2-finger swipe right
                - 'forward': 2-finger swipe left
                - 'zoom_in': Pinch out
                - 'zoom_out': Pinch in
        """
        actions = {
            'next_tab': lambda: self.trackpad_swipe('left', fingers=3),
            'prev_tab': lambda: self.trackpad_swipe('right', fingers=3),
            'back': lambda: self.trackpad_swipe('right', fingers=2),
            'forward': lambda: self.trackpad_swipe('left', fingers=2),
            'zoom_in': lambda: self.trackpad_pinch(1.5),
            'zoom_out': lambda: self.trackpad_pinch(0.7),
        }
        
        if action in actions:
            actions[action]()
        else:
            raise ValueError(f"Unknown VSCode gesture action: {action}")
    
    def natural_scroll_reading(self, lines: int = 10) -> None:
        """Simulate natural reading scroll pattern.
        
        Args:
            lines: Approximate number of lines to scroll
        """
        # Vary scroll speed and add pauses like reading
        for _ in range(lines):
            # Random scroll amount per "line"
            scroll_amount = random.randint(3, 7)
            self.trackpad_scroll(0, scroll_amount, smooth=True)
            
            # Random pause as if reading
            if random.random() < 0.3:  # 30% chance of pause
                time.sleep(random.uniform(0.5, 2.0))
            else:
                time.sleep(random.uniform(0.1, 0.3))