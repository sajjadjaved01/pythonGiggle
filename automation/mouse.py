"""Enhanced mouse movement patterns for natural automation."""

import math
import time
import random
from typing import Tuple, List, Optional
import pyautogui


class NaturalMouseController:
    """Advanced mouse movement with human-like patterns."""
    
    def __init__(self, config: dict = None):
        """Initialize mouse controller with configuration."""
        self.config = config or {}
        self.screen_width, self.screen_height = pyautogui.size()
        
        # Movement parameters
        self.base_speed = self.config.get('base_speed', 500)  # pixels per second
        self.speed_variance = self.config.get('speed_variance', 0.3)
        self.micro_movement_enabled = self.config.get('micro_movements', True)
        self.overshoot_probability = self.config.get('overshoot_probability', 0.2)
        self.overshoot_distance = self.config.get('overshoot_distance', 0.1)  # 10% of distance
    
    def bezier_curve(self, start: Tuple[int, int], end: Tuple[int, int], 
                     control_points: int = 2, steps: int = 50) -> List[Tuple[float, float]]:
        """Generate Bézier curve path between two points.
        
        Args:
            start: Starting coordinates (x, y)
            end: Ending coordinates (x, y)
            control_points: Number of control points
            steps: Number of steps in the curve
            
        Returns:
            List of (x, y) coordinates along the curve
        """
        # Generate random control points
        controls = []
        for i in range(control_points):
            # Control points are offset from the straight line
            t = (i + 1) / (control_points + 1)
            mid_x = start[0] + (end[0] - start[0]) * t
            mid_y = start[1] + (end[1] - start[1]) * t
            
            # Add random offset
            offset_range = math.sqrt((end[0] - start[0])**2 + (end[1] - start[1])**2) * 0.2
            offset_x = random.uniform(-offset_range, offset_range)
            offset_y = random.uniform(-offset_range, offset_range)
            
            controls.append((mid_x + offset_x, mid_y + offset_y))
        
        # Create curve points
        points = [start] + controls + [end]
        curve = []
        
        for step in range(steps + 1):
            t = step / steps
            x, y = self._bezier_point(points, t)
            curve.append((x, y))
        
        return curve
    
    def _bezier_point(self, points: List[Tuple[float, float]], t: float) -> Tuple[float, float]:
        """Calculate a point on the Bézier curve using De Casteljau's algorithm."""
        if len(points) == 1:
            return points[0]
        
        new_points = []
        for i in range(len(points) - 1):
            x = points[i][0] * (1 - t) + points[i + 1][0] * t
            y = points[i][1] * (1 - t) + points[i + 1][1] * t
            new_points.append((x, y))
        
        return self._bezier_point(new_points, t)
    
    def bezier_move(self, x: int, y: int, duration: Optional[float] = None) -> None:
        """Move mouse using Bézier curve with human-like characteristics.
        
        Args:
            x: Target x coordinate
            y: Target y coordinate
            duration: Movement duration (calculated if not provided)
        """
        start_x, start_y = pyautogui.position()
        distance = math.sqrt((x - start_x)**2 + (y - start_y)**2)
        
        # Calculate duration based on distance if not provided
        if duration is None:
            # Fitts's Law inspired timing
            duration = 0.2 + (distance / self.base_speed) * random.uniform(1 - self.speed_variance, 1 + self.speed_variance)
        
        # Determine if we should overshoot
        overshoot = random.random() < self.overshoot_probability and distance > 50
        
        if overshoot:
            # Calculate overshoot position
            overshoot_dist = distance * self.overshoot_distance
            angle = math.atan2(y - start_y, x - start_x)
            overshoot_x = x + math.cos(angle) * overshoot_dist
            overshoot_y = y + math.sin(angle) * overshoot_dist
            
            # Move to overshoot position first
            curve = self.bezier_curve((start_x, start_y), (overshoot_x, overshoot_y), control_points=2)
            self._execute_curve(curve, duration * 0.8)
            
            # Then correct to actual position
            curve = self.bezier_curve((overshoot_x, overshoot_y), (x, y), control_points=1)
            self._execute_curve(curve, duration * 0.2)
        else:
            # Direct movement with curve
            control_points = 1 if distance < 100 else 2
            curve = self.bezier_curve((start_x, start_y), (x, y), control_points=control_points)
            self._execute_curve(curve, duration)
    
    def _execute_curve(self, curve: List[Tuple[float, float]], duration: float) -> None:
        """Execute mouse movement along a curve."""
        steps = len(curve) - 1
        step_duration = duration / steps
        
        for i, (x, y) in enumerate(curve):
            # Add micro movements for realism
            if self.micro_movement_enabled and i > 0 and i < steps:
                x += random.uniform(-1, 1)
                y += random.uniform(-1, 1)
            
            pyautogui.moveTo(x, y, duration=0, _pause=False)
            
            # Variable speed - slower at start and end
            progress = i / steps
            speed_multiplier = 1.0 - 4 * (progress - 0.5) ** 2  # Parabolic speed curve
            time.sleep(step_duration * speed_multiplier)
    
    def micro_movement(self, duration: float = 0.5) -> None:
        """Perform small random mouse movements to simulate hand tremor."""
        start_time = time.time()
        original_x, original_y = pyautogui.position()
        
        while time.time() - start_time < duration:
            # Small random offset
            offset_x = random.gauss(0, 2)  # Gaussian distribution for more natural movement
            offset_y = random.gauss(0, 2)
            
            # Ensure we don't drift too far
            new_x = original_x + max(-5, min(5, offset_x))
            new_y = original_y + max(-5, min(5, offset_y))
            
            pyautogui.moveTo(new_x, new_y, duration=0.05)
            time.sleep(random.uniform(0.05, 0.15))
    
    def hesitation_move(self, x: int, y: int, hesitation_points: int = 1) -> None:
        """Move to target with hesitation points along the way.
        
        Args:
            x: Target x coordinate
            y: Target y coordinate
            hesitation_points: Number of hesitation points
        """
        start_x, start_y = pyautogui.position()
        
        # Create waypoints including hesitations
        waypoints = [(start_x, start_y)]
        
        for i in range(hesitation_points):
            t = (i + 1) / (hesitation_points + 1)
            way_x = start_x + (x - start_x) * t
            way_y = start_y + (y - start_y) * t
            
            # Add slight offset to waypoint
            way_x += random.uniform(-20, 20)
            way_y += random.uniform(-20, 20)
            waypoints.append((way_x, way_y))
        
        waypoints.append((x, y))
        
        # Move through waypoints with pauses
        for i in range(len(waypoints) - 1):
            self.bezier_move(waypoints[i + 1][0], waypoints[i + 1][1])
            
            # Hesitate at intermediate points
            if i < len(waypoints) - 2:
                self.micro_movement(random.uniform(0.1, 0.3))
                time.sleep(random.uniform(0.1, 0.5))
    
    def natural_click(self, x: Optional[int] = None, y: Optional[int] = None, 
                     double: bool = False) -> None:
        """Perform natural mouse click with human-like characteristics.
        
        Args:
            x: X coordinate (current position if None)
            y: Y coordinate (current position if None)
            double: Perform double-click
        """
        if x is not None and y is not None:
            self.bezier_move(x, y)
        
        # Small movement before click (hand adjustment)
        self.micro_movement(0.1)
        
        # Variable click duration
        click_duration = random.uniform(0.05, 0.15)
        
        if double:
            pyautogui.click(clicks=2, interval=random.uniform(0.05, 0.15))
        else:
            pyautogui.mouseDown()
            time.sleep(click_duration)
            pyautogui.mouseUp()
    
    def drag_with_curve(self, start_x: int, start_y: int, end_x: int, end_y: int,
                       duration: float = 1.0) -> None:
        """Perform drag operation with curved path.
        
        Args:
            start_x, start_y: Starting coordinates
            end_x, end_y: Ending coordinates
            duration: Total drag duration
        """
        # Move to start position
        self.bezier_move(start_x, start_y)
        time.sleep(0.1)
        
        # Press mouse button
        pyautogui.mouseDown()
        
        # Generate curve for drag
        curve = self.bezier_curve((start_x, start_y), (end_x, end_y), control_points=2)
        
        # Execute drag along curve
        for i, (x, y) in enumerate(curve[1:], 1):
            progress = i / len(curve)
            pyautogui.moveTo(x, y, duration=0)
            time.sleep(duration / len(curve))
        
        # Release mouse button
        time.sleep(0.1)
        pyautogui.mouseUp()
    
    def hover_and_wait(self, x: int, y: int, wait_time: float = 1.0) -> None:
        """Move to position and hover with micro movements.
        
        Args:
            x: Target x coordinate
            y: Target y coordinate
            wait_time: Time to hover in seconds
        """
        self.bezier_move(x, y)
        self.micro_movement(wait_time)