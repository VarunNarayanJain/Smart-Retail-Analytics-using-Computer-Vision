"""
Zone Selection Tool for Store Boundary Definition

This module allows users to interactively define a store zone by clicking
points on the video frame. The zone is used to determine occupancy by checking
if people are inside the defined boundary.

Author: Smart Retail Analytics Team
"""

import cv2
import numpy as np
import json
from pathlib import Path


class ZoneSelector:
    """
    Interactive zone selection tool using mouse clicks.
    
    User clicks points on the frame to define a polygon boundary.
    The polygon represents the store area for occupancy tracking.
    """
    
    def __init__(self, frame, window_name="Zone Selection"):
        """
        Initialize zone selector with a frame.
        
        Args:
            frame: First frame of video to draw zone on
            window_name: Name of the OpenCV window
        """
        self.frame = frame.copy()
        self.original_frame = frame.copy()
        self.window_name = window_name
        self.points = []
        self.complete = False
        
    def _mouse_callback(self, event, x, y, flags, param):
        """
        Handle mouse events for zone selection.
        
        LEFT CLICK: Add point to polygon
        RIGHT CLICK: Complete polygon (minimum 3 points)
        """
        if event == cv2.EVENT_LBUTTONDOWN:
            # Add point
            self.points.append((x, y))
            print(f"✓ Point {len(self.points)}: ({x}, {y})")
            
            # Redraw frame with updated points
            self._draw_zone()
            
        elif event == cv2.EVENT_RBUTTONDOWN:
            # Complete polygon
            if len(self.points) >= 3:
                self.complete = True
                print(f"✅ Zone completed with {len(self.points)} points!")
            else:
                print(f"⚠️  Need at least 3 points (current: {len(self.points)})")
    
    def _draw_zone(self):
        """Draw current zone on frame."""
        # Reset frame
        self.frame = self.original_frame.copy()
        
        # Draw points
        for i, point in enumerate(self.points):
            cv2.circle(self.frame, point, 5, (0, 255, 0), -1)
            cv2.putText(self.frame, str(i+1), 
                       (point[0]+10, point[1]-10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        # Draw lines between points
        if len(self.points) > 1:
            for i in range(len(self.points) - 1):
                cv2.line(self.frame, self.points[i], self.points[i+1], 
                        (0, 255, 255), 2)
        
        # Draw polygon if complete
        if self.complete and len(self.points) >= 3:
            pts = np.array(self.points, np.int32)
            pts = pts.reshape((-1, 1, 2))
            cv2.polylines(self.frame, [pts], True, (0, 255, 0), 3)
            
            # Fill with semi-transparent overlay
            overlay = self.frame.copy()
            cv2.fillPoly(overlay, [pts], (0, 255, 0))
            cv2.addWeighted(overlay, 0.2, self.frame, 0.8, 0, self.frame)
        
        # Display instructions
        self._draw_instructions()
        
        cv2.imshow(self.window_name, self.frame)
    
    def _draw_instructions(self):
        """Draw instruction text on frame."""
        instructions = [
            "ZONE SELECTION MODE",
            "Left Click: Add point",
            "Right Click: Complete zone (min 3 points)",
            f"Points: {len(self.points)}"
        ]
        
        y_offset = 30
        for i, text in enumerate(instructions):
            color = (0, 255, 0) if i == 0 else (255, 255, 255)
            thickness = 2 if i == 0 else 1
            cv2.putText(self.frame, text, (10, y_offset + i*25),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, thickness)
    
    def select_zone(self):
        """
        Start interactive zone selection.
        
        Returns:
            list: List of (x, y) tuples defining the polygon
                 Returns None if cancelled
        """
        print("\n" + "="*60)
        print("ZONE SELECTION MODE")
        print("="*60)
        print("Instructions:")
        print("  • Left Click: Add point to define store boundary")
        print("  • Right Click: Complete zone (minimum 3 points required)")
        print("  • Press 'r': Reset and start over")
        print("  • Press 'q': Cancel and quit")
        print("="*60 + "\n")
        
        cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(self.window_name, 1280, 720)
        cv2.setMouseCallback(self.window_name, self._mouse_callback)
        
        self._draw_zone()
        
        while True:
            key = cv2.waitKey(1) & 0xFF
            
            if key == ord('q'):
                print("❌ Zone selection cancelled")
                cv2.destroyWindow(self.window_name)
                return None
            
            elif key == ord('r'):
                print("🔄 Resetting points...")
                self.points = []
                self.complete = False
                self._draw_zone()
            
            elif self.complete:
                cv2.destroyWindow(self.window_name)
                return self.points
        
    @staticmethod
    def save_zone(zone_points, video_path, zones_dir="zones"):
        """
        Save zone coordinates to JSON file.
        
        Args:
            zone_points: List of (x, y) tuples
            video_path: Path to video file
            zones_dir: Directory to save zone files
        
        Returns:
            str: Path to saved zone file
        """
        # Create zones directory
        zones_path = Path(zones_dir)
        zones_path.mkdir(exist_ok=True)
        
        # Generate zone filename from video name
        video_name = Path(video_path).stem
        zone_file = zones_path / f"{video_name}_zone.json"
        
        # Save zone data
        zone_data = {
            "video": str(video_path),
            "points": zone_points,
            "num_points": len(zone_points)
        }
        
        with open(zone_file, 'w') as f:
            json.dump(zone_data, f, indent=2)
        
        print(f"💾 Zone saved to: {zone_file}")
        return str(zone_file)
    
    @staticmethod
    def load_zone(video_path, zones_dir="zones"):
        """
        Load zone coordinates from JSON file.
        
        Args:
            video_path: Path to video file
            zones_dir: Directory containing zone files
        
        Returns:
            list: List of (x, y) tuples, or None if not found
        """
        video_name = Path(video_path).stem
        zone_file = Path(zones_dir) / f"{video_name}_zone.json"
        
        if zone_file.exists():
            with open(zone_file, 'r') as f:
                zone_data = json.load(f)
            
            print(f"📂 Zone loaded from: {zone_file}")
            print(f"   Points: {zone_data['num_points']}")
            return zone_data['points']
        
        return None
    
    @staticmethod
    def point_in_polygon(point, polygon):
        """
        Check if a point is inside a polygon using ray casting algorithm.
        
        Args:
            point: (x, y) tuple
            polygon: List of (x, y) tuples defining polygon vertices
        
        Returns:
            bool: True if point is inside polygon
        """
        # Use OpenCV's built-in function (optimized)
        poly_np = np.array(polygon, np.int32)
        result = cv2.pointPolygonTest(poly_np, point, False)
        return result >= 0  # Inside or on boundary
    
    @staticmethod
    def draw_zone_on_frame(frame, zone_points, color=(0, 255, 0), thickness=2, 
                           fill=True, alpha=0.2):
        """
        Draw zone polygon on frame.
        
        Args:
            frame: Frame to draw on
            zone_points: List of (x, y) tuples
            color: BGR color tuple
            thickness: Line thickness
            fill: Whether to fill polygon with transparent overlay
            alpha: Transparency of fill (0=transparent, 1=opaque)
        
        Returns:
            frame: Frame with zone drawn
        """
        if not zone_points or len(zone_points) < 3:
            return frame
        
        pts = np.array(zone_points, np.int32)
        pts = pts.reshape((-1, 1, 2))
        
        # Draw polygon outline
        cv2.polylines(frame, [pts], True, color, thickness)
        
        # Fill with semi-transparent overlay
        if fill:
            overlay = frame.copy()
            cv2.fillPoly(overlay, [pts], color)
            cv2.addWeighted(overlay, alpha, frame, 1-alpha, 0, frame)
        
        return frame
