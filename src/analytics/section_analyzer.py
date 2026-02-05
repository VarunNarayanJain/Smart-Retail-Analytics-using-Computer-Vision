"""
Section-Based Analytics Module

This module tracks occupancy across multiple defined sections of the store.
It builds on the zone-based occupancy tracking from Phase 4.

Key Features:
- Track multiple sections simultaneously (Electronics, Clothing, etc.)
- Per-section occupancy counting
- Per-section peak tracking
- Section-wise analytics and reporting

Author: Smart Retail Analytics Team
Phase: 5 - Advanced Analytics
"""

import numpy as np
import cv2
from datetime import datetime
from pathlib import Path
import sys

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))
from config import *
from utils.zone_selector import ZoneSelector


class SectionAnalyzer:
    """
    Analyzes occupancy across multiple defined sections of the store.
    
    Each section is a polygon zone. People are counted in each section
    independently, allowing for detailed spatial analytics.
    
    Attributes:
        sections: List of section definitions with names and polygon points
        section_occupancy: Current occupancy per section
        section_peaks: Peak occupancy per section
        section_history: Historical occupancy data per section
    """
    
    def __init__(self, sections, frame_width, frame_height, enable_logging=True):
        """
        Initialize the Section Analyzer.
        
        Args:
            sections: List of dicts with 'name' and 'points' keys
                     Example: [
                         {"name": "Electronics", "points": [(x1,y1), (x2,y2)...]},
                         {"name": "Clothing", "points": [(x1,y1), (x2,y2)...]}
                     ]
            frame_width: Width of video frame
            frame_height: Height of video frame
            enable_logging: Enable CSV logging
        """
        self.sections = sections
        self.frame_width = frame_width
        self.frame_height = frame_height
        self.enable_logging = enable_logging
        
        # Initialize tracking dictionaries
        self.section_occupancy = {}      # Current count per section
        self.section_peaks = {}          # Peak count per section
        self.section_totals = {}         # Running total for averaging
        self.section_people = {}         # Set of track IDs per section
        self.section_history = {}        # Frame-by-frame history
        
        # Initialize for each section
        for section in sections:
            name = section['name']
            self.section_occupancy[name] = 0
            self.section_peaks[name] = 0
            self.section_totals[name] = 0
            self.section_people[name] = set()
            self.section_history[name] = []
        
        self.frame_count = 0
        self.start_time = datetime.now()
        
        # Setup logging
        if self.enable_logging:
            self.log_file = REPORTS_DIR / "logs" / "section_analysis.csv"
            self.log_file.parent.mkdir(parents=True, exist_ok=True)
            self._init_log_file()
        
        print(f"✅ Section Analyzer initialized with {len(sections)} sections")
    
    def _init_log_file(self):
        """Initialize CSV log file with headers."""
        with open(self.log_file, 'w') as f:
            f.write("timestamp,frame,section,occupancy,peak,event,track_ids\n")
    
    def update(self, tracked_objects, frame_num):
        """
        Update section occupancy based on tracked objects.
        
        Args:
            tracked_objects: List of tracked person objects with 'center' and 'id'
            frame_num: Current frame number
        
        Returns:
            dict: Statistics for all sections
        """
        self.frame_count = frame_num
        
        # Reset current occupancy
        for name in self.section_occupancy.keys():
            self.section_people[name] = set()
        
        # Check which section each person is in
        for obj in tracked_objects:
            cx, cy = obj['center']
            track_id = obj['id']
            
            # Check against each section
            for section in self.sections:
                name = section['name']
                points = section['points']
                
                # Check if person is inside this section
                if ZoneSelector.point_in_polygon((cx, cy), points):
                    self.section_people[name].add(track_id)
        
        # Update occupancy counts and peaks
        for name in self.section_occupancy.keys():
            current_count = len(self.section_people[name])
            self.section_occupancy[name] = current_count
            self.section_totals[name] += current_count
            
            # Update peak
            if current_count > self.section_peaks[name]:
                self.section_peaks[name] = current_count
                if self.enable_logging:
                    self._log_event(name, current_count, "peak", self.section_people[name])
            
            # Store history
            self.section_history[name].append(current_count)
            
            # Log updates periodically (every 30 frames)
            if self.enable_logging and frame_num % 30 == 0:
                self._log_event(name, current_count, "update", self.section_people[name])
        
        return self.get_statistics()
    
    def _log_event(self, section_name, occupancy, event, track_ids):
        """Log a section event to CSV."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        track_ids_str = "|".join(map(str, track_ids))
        peak = self.section_peaks[section_name]
        
        with open(self.log_file, 'a') as f:
            f.write(f"{timestamp},{self.frame_count},{section_name},{occupancy},{peak},{event},{track_ids_str}\n")
    
    def get_statistics(self):
        """
        Get current statistics for all sections.
        
        Returns:
            dict: Statistics including current occupancy, peaks, and averages
        """
        stats = {
            'sections': {}
        }
        
        for name in self.section_occupancy.keys():
            avg = self.section_totals[name] / self.frame_count if self.frame_count > 0 else 0
            
            stats['sections'][name] = {
                'current': self.section_occupancy[name],
                'peak': self.section_peaks[name],
                'average': avg,
                'track_ids': list(self.section_people[name])
            }
        
        return stats
    
    def draw_sections(self, frame):
        """
        Draw all section boundaries on the frame.
        
        Args:
            frame: Video frame to draw on
        
        Returns:
            frame: Frame with sections drawn
        """
        # Colors for different sections (cycle through these)
        colors = [
            (255, 0, 255),    # Magenta
            (0, 255, 255),    # Cyan
            (255, 255, 0),    # Yellow
            (255, 128, 0),    # Orange
            (128, 0, 255),    # Purple
            (0, 255, 128),    # Spring Green
        ]
        
        for idx, section in enumerate(self.sections):
            name = section['name']
            points = section['points']
            color = colors[idx % len(colors)]
            
            # Draw polygon
            pts = np.array(points, dtype=np.int32)
            cv2.polylines(frame, [pts], isClosed=True, color=color, thickness=2)
            
            # Draw section name and occupancy
            # Find centroid for label placement
            M = cv2.moments(pts)
            if M['m00'] != 0:
                cx = int(M['m10'] / M['m00'])
                cy = int(M['m01'] / M['m00'])
            else:
                cx, cy = points[0]
            
            # Background for text
            occupancy = self.section_occupancy.get(name, 0)
            label = f"{name}: {occupancy}"
            (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
            
            cv2.rectangle(frame, (cx - 10, cy - th - 10), 
                         (cx + tw + 10, cy + 5), color, -1)
            cv2.putText(frame, label, (cx, cy), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        return frame
    
    def draw_stats(self, frame, position='bottom-left'):
        """
        Draw section statistics overlay on frame.
        
        Args:
            frame: Video frame
            position: Where to draw stats ('top-left', 'bottom-left', etc.)
        
        Returns:
            frame: Frame with stats overlay
        """
        h, w = frame.shape[:2]
        
        # Calculate position
        if position == 'bottom-left':
            start_x, start_y = 10, h - 20
            direction = -1  # Draw upwards
        else:  # top-left
            start_x, start_y = 10, 30
            direction = 1   # Draw downwards
        
        y_offset = start_y
        line_height = 30
        
        # Header
        cv2.putText(frame, "SECTION ANALYTICS", (start_x, y_offset),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
        y_offset += line_height * direction
        
        # Stats for each section
        for name, data in self.get_statistics()['sections'].items():
            text = f"{name}: {data['current']} (Peak: {data['peak']})"
            cv2.putText(frame, text, (start_x, y_offset),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            y_offset += line_height * direction
        
        return frame
    
    def print_summary(self):
        """Print comprehensive summary of section analytics."""
        print("\n" + "="*60)
        print("SECTION ANALYTICS SUMMARY")
        print("="*60)
        
        stats = self.get_statistics()
        
        for name, data in stats['sections'].items():
            print(f"\n📍 {name}:")
            print(f"   Current Occupancy:  {data['current']}")
            print(f"   Peak Occupancy:     {data['peak']}")
            print(f"   Average Occupancy:  {data['average']:.1f}")
        
        # Overall statistics
        total_current = sum(d['current'] for d in stats['sections'].values())
        total_peak = sum(d['peak'] for d in stats['sections'].values())
        
        print(f"\n📊 Overall:")
        print(f"   Total Current:      {total_current}")
        print(f"   Total Peaks Sum:    {total_peak}")
        print(f"   Frames Processed:   {self.frame_count}")
        
        if self.enable_logging:
            print(f"\n📋 Log File: {self.log_file}")
        
        print("="*60)
