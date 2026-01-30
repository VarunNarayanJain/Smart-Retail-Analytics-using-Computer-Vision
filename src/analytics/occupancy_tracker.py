"""
Zone-Based Occupancy Tracking Module

This module tracks the number of people inside a defined store zone.
Unlike line-crossing detection, this approach counts people based on
whether their position is inside a polygon boundary.

Author: Smart Retail Analytics Team
"""

import cv2
import numpy as np
from datetime import datetime
from collections import defaultdict
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))
from config import *
from utils.zone_selector import ZoneSelector


class OccupancyTracker:
    """
    Track store occupancy based on people inside a defined zone.
    
    This replaces the line-crossing approach with a simpler geometric
    containment check: if person is inside zone → count as occupant.
    
    FEATURES:
    - Real-time occupancy count
    - Initial occupancy detection
    - Detailed logging (CSV)
    - Visual overlay (zone + count)
    - Analytics (peak times, average occupancy)
    """
    
    def __init__(self, frame_height, frame_width, zone_points,
                 enable_logging=True):
        """
        Initialize occupancy tracker with zone definition.
        
        Args:
            frame_height: Height of video frame
            frame_width: Width of video frame
            zone_points: List of (x, y) tuples defining store boundary
            enable_logging: Whether to log events to CSV
        """
        self.frame_height = frame_height
        self.frame_width = frame_width
        self.zone_points = zone_points
        
        # Tracking state
        self.people_inside = set()  # Set of track IDs currently inside zone
        self.track_history = defaultdict(list)  # Track positions over time
        
        # Statistics
        self.max_occupancy = 0
        self.occupancy_history = []  # List of (timestamp, count) tuples
        self.start_time = datetime.now()
        self.frame_count = 0
        
        # Initial occupancy detection
        self.initial_detection_complete = False
        
        # Logging
        self.enable_logging = enable_logging
        self.log_file = REPORTS_DIR / "logs" / "occupancy_log.csv"
        
        if enable_logging:
            self._initialize_log_file()
        
        print(f"\n{'='*60}")
        print("OCCUPANCY TRACKER INITIALIZED - ZONE-BASED MODE")
        print(f"{'='*60}")
        print(f"Frame Size: {frame_width}x{frame_height}")
        print(f"Zone Points: {len(zone_points)}")
        print(f"Logging: {'Enabled' if enable_logging else 'Disabled'}")
        print(f"{'='*60}\n")
    
    def _initialize_log_file(self):
        """Create CSV log file with headers."""
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(self.log_file, 'w') as f:
            f.write("timestamp,frame,occupancy,max_occupancy,event,track_id\n")
        
        print(f"📝 Occupancy log: {self.log_file}")
    
    def _log_event(self, frame_num, occupancy, event="", track_id=""):
        """
        Log occupancy data to CSV.
        
        Args:
            frame_num: Current frame number
            occupancy: Current occupancy count
            event: Event type (entry/exit/update)
            track_id: Track ID involved in event
        """
        if not self.enable_logging:
            return
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        with open(self.log_file, 'a') as f:
            f.write(f"{timestamp},{frame_num},{occupancy},{self.max_occupancy},{event},{track_id}\n")
    
    def update(self, tracked_objects, frame_num):
        """
        Update occupancy based on tracked people.
        
        Args:
            tracked_objects: List of tracked objects from tracker
                Each: {'id', 'bbox', 'center', ...}
            frame_num: Current frame number
        
        Returns:
            dict: Current statistics
        """
        self.frame_count = frame_num
        
        # Current frame occupants
        current_inside = set()
        
        # Check each tracked person
        for obj in tracked_objects:
            track_id = obj['id']
            bbox = obj['bbox']
            
            # Get center point
            x, y, w, h = bbox
            center_x = int(x + w / 2)
            center_y = int(y + h / 2)
            
            # Check if inside zone
            is_inside = ZoneSelector.point_in_polygon(
                (center_x, center_y), 
                self.zone_points
            )
            
            if is_inside:
                current_inside.add(track_id)
                
                # New person entered zone
                if track_id not in self.people_inside:
                    if self.initial_detection_complete:
                        print(f"🟢 ENTRY: ID {track_id} | Frame {frame_num} | Time {datetime.now().strftime('%H:%M:%S')}")
                        self._log_event(frame_num, len(current_inside), "entry", track_id)
        
        # Detect people who left zone
        for track_id in self.people_inside:
            if track_id not in current_inside:
                if self.initial_detection_complete:
                    print(f"🔴 EXIT: ID {track_id} | Frame {frame_num} | Time {datetime.now().strftime('%H:%M:%S')}")
                    self._log_event(frame_num, len(current_inside), "exit", track_id)
        
        # Handle initial occupancy detection
        if not self.initial_detection_complete and frame_num >= 5:
            if len(current_inside) > 0:
                print(f"\n🔵 INITIAL OCCUPANCY: {len(current_inside)} people inside store")
                for tid in current_inside:
                    print(f"  ↳ ID {tid} counted as initial occupant")
                print()
            
            self.initial_detection_complete = True
            self._log_event(frame_num, len(current_inside), "initial", "")
        
        # Update state
        self.people_inside = current_inside
        occupancy = len(self.people_inside)
        
        # Update statistics
        if occupancy > self.max_occupancy:
            self.max_occupancy = occupancy
        
        self.occupancy_history.append((datetime.now(), occupancy))
        
        # Periodic logging (every 30 frames)
        if frame_num % 30 == 0:
            self._log_event(frame_num, occupancy, "update", "")
        
        return {
            'occupancy': occupancy,
            'max_occupancy': self.max_occupancy,
            'people_inside': list(self.people_inside)
        }
    
    def draw_zone(self, frame):
        """
        Draw zone boundary on frame.
        
        Args:
            frame: Video frame to draw on
        
        Returns:
            frame: Frame with zone visualization
        """
        frame = ZoneSelector.draw_zone_on_frame(
            frame, 
            self.zone_points,
            color=(0, 255, 255),  # Yellow
            thickness=3,
            fill=True,
            alpha=0.15
        )
        
        # Add zone label
        if len(self.zone_points) > 0:
            # Find topmost point for label
            top_point = min(self.zone_points, key=lambda p: p[1])
            cv2.putText(frame, "STORE ZONE", 
                       (top_point[0], top_point[1] - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
        
        return frame
    
    def draw_stats(self, frame, position='top-right'):
        """
        Draw occupancy statistics on frame.
        
        Args:
            frame: Video frame
            position: Where to draw stats ('top-right', 'top-left', etc.)
        
        Returns:
            frame: Frame with stats overlay
        """
        occupancy = len(self.people_inside)
        
        # Prepare stats text
        stats = [
            f"Occupancy: {occupancy}",
            f"Peak: {self.max_occupancy}",
            f"IDs: {sorted(list(self.people_inside))[:5]}" + ("..." if occupancy > 5 else "")
        ]
        
        # Calculate position
        h, w = frame.shape[:2]
        if position == 'top-right':
            x, y = w - 300, 40
        elif position == 'top-left':
            x, y = 20, 40
        elif position == 'bottom-right':
            x, y = w - 300, h - 100
        else:  # bottom-left
            x, y = 20, h - 100
        
        # Draw semi-transparent background
        overlay = frame.copy()
        cv2.rectangle(overlay, (x-10, y-30), (x+280, y+len(stats)*35+10), 
                     (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.6, frame, 0.4, 0, frame)
        
        # Draw stats text
        for i, stat in enumerate(stats):
            color = (0, 255, 0) if i == 0 else (255, 255, 255)
            thickness = 2 if i == 0 else 1
            cv2.putText(frame, stat, (x, y + i*35),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, thickness)
        
        return frame
    
    def get_statistics(self):
        """
        Get comprehensive statistics.
        
        Returns:
            dict: Statistics summary
        """
        duration = (datetime.now() - self.start_time).total_seconds()
        
        # Calculate average occupancy
        avg_occupancy = 0
        if self.occupancy_history:
            avg_occupancy = sum(o for _, o in self.occupancy_history) / len(self.occupancy_history)
        
        return {
            'current_occupancy': len(self.people_inside),
            'max_occupancy': self.max_occupancy,
            'avg_occupancy': round(avg_occupancy, 1),
            'duration_seconds': round(duration, 1),
            'total_frames': self.frame_count,
            'people_inside_ids': list(self.people_inside)
        }
    
    def print_summary(self):
        """Print final statistics summary."""
        stats = self.get_statistics()
        
        print(f"\n{'='*60}")
        print("OCCUPANCY TRACKING SUMMARY")
        print(f"{'='*60}")
        print(f"👥 Current Occupancy:   {stats['current_occupancy']}")
        print(f"📊 Peak Occupancy:      {stats['max_occupancy']}")
        print(f"📈 Average Occupancy:   {stats['avg_occupancy']}")
        print(f"⏱  Duration:            {stats['duration_seconds']:.1f} seconds")
        print(f"🎬 Total Frames:        {stats['total_frames']}")
        print(f"📋 Log File:            {self.log_file}")
        print(f"{'='*60}\n")
