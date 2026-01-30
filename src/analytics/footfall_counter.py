"""
PHASE 4: FOOTFALL COUNTER
=========================

This module implements footfall counting - tracking unique entries and exits in a retail space.

KEY CONCEPTS:
-------------
1. **Virtual Lines**: Imaginary lines across the video frame (like laser beams!)
   - Entry line: Typically near the entrance (top of frame)
   - Exit line: Typically near the exit (bottom of frame)
   
2. **Line Crossing Detection**: Detecting when a tracked person crosses these lines
   - We track the CENTER POINT of each person's bounding box
   - When center moves from one side of line to the other = CROSSING!
   
3. **Direction Analysis**: Determining if person is entering or exiting
   - Crossing entry line downward (top→bottom) = ENTRY
   - Crossing exit line upward (bottom→top) = EXIT
   
4. **Unique Counting**: Using tracking IDs ensures we count PEOPLE, not detections
   - ID:0 crosses entry = 1 entry (not 30 entries from 30 frames!)
   - Same ID can't be counted twice for same event
   
5. **Occupancy Tracking**: Real-time count of people currently in store
   - Occupancy = Total Entries - Total Exits
   - Useful for capacity management

ALGORITHM OVERVIEW:
-------------------
For each frame:
    1. Get tracked persons with their IDs and bounding boxes
    2. Calculate center point (cx, cy) of each box
    3. Check if center crossed entry/exit lines since last frame
    4. Determine crossing direction (up or down)
    5. Log the event with timestamp
    6. Update entry/exit counters
    7. Calculate current occupancy

DATA STRUCTURES:
----------------
- track_history: Dictionary mapping track_id → list of (y_position, frame_num)
  Example: {0: [(450, 1), (455, 2), (460, 3)], 1: [(200, 1), (205, 2)]}
  Used to: Track movement history for direction analysis

- counted_entries: Set of track IDs that have been counted as entries
  Example: {0, 2, 5}
  Used to: Prevent double-counting same person

- counted_exits: Set of track IDs that have been counted as exits
  Example: {0, 3}
  Used to: Prevent double-counting same person

- event_log: List of all entry/exit events with details
  Example: [{'id': 0, 'type': 'entry', 'time': '10:05:32', 'frame': 150}]
  Used to: Generate reports and analyze patterns

MATHEMATICAL CONCEPTS:
----------------------
1. Line Crossing Detection:
   - Line at y = L (horizontal line)
   - Person center at y_prev and y_curr
   - Crossing = (y_prev < L and y_curr >= L) or (y_prev >= L and y_curr < L)
   
2. Direction Determination:
   - Downward: y_curr > y_prev (increasing y = moving down)
   - Upward: y_curr < y_prev (decreasing y = moving up)
   
3. Occupancy Calculation:
   - Occupancy = len(people_inside)
   - people_inside = entered_ids - exited_ids

WHY THIS MATTERS:
-----------------
Traditional motion sensors: Count every movement (unreliable)
Our system: Counts unique people with direction (accurate!)

Example:
- Person walks in, browses, walks out = 1 entry, 1 exit ✅
- Motion sensor would count: 1000+ movements ❌

Real-world applications:
- Retail: Conversion rate = Purchases / Unique Visitors
- Events: Attendance tracking
- Security: Occupancy limits enforcement
- Marketing: Peak hour analysis
"""

import cv2
import numpy as np
from datetime import datetime
import csv
from pathlib import Path
from collections import defaultdict, deque

# Import configurations
import sys
sys.path.append(str(Path(__file__).parent.parent.parent))
from src.config import (
    ENTRANCE_LINE_POSITION,
    ENTRANCE_LINE_ORIENTATION,
    REVERSE_ENTRY_DIRECTION,
    LINE_THICKNESS,
    LINE_COLOR_ENTRANCE,
    CROSSING_BUFFER,
    MIN_FRAMES_FOR_DIRECTION,
    FOOTFALL_DEBUG_MODE,
    INSIDE_ZONE_POSITION,
    ENABLE_FOOTFALL_LOGGING,
    FOOTFALL_LOG_FILE,
    REPORTS_DIR
)


class FootfallCounter:
    """
    Footfall Counter - Tracks entries and exits in a retail space
    
    This class analyzes tracked persons and detects when they cross virtual
    entry/exit lines. It maintains counts, logs events, and tracks occupancy.
    
    DESIGN PHILOSOPHY:
    ------------------
    - Each tracked person (ID) has a movement history
    - We analyze this history to detect line crossings
    - Direction is determined by comparing current vs previous positions
    - Events are logged for later analysis
    - Double-counting is prevented using sets
    
    TYPICAL USAGE:
    --------------
    ```python
    counter = FootfallCounter(frame_height=720, frame_width=1280)
    
    for frame in video:
        tracked_objects = tracker.update(detections)
        counter.update(tracked_objects, frame_number)
        
        # Draw visualization
        frame = counter.draw_lines(frame)
        frame = counter.draw_stats(frame)
        
    # Get final statistics
    stats = counter.get_statistics()
    counter.save_log()
    ```
    """
    
    def __init__(self, frame_height, frame_width, 
                 entrance_line_pos=None,
                 entrance_line_orientation=None,
                 enable_logging=ENABLE_FOOTFALL_LOGGING):
        """
        Initialize the footfall counter
        
        Args:
            frame_height (int): Height of video frame in pixels
            frame_width (int): Width of video frame in pixels
            entrance_line_pos (float): Entrance line position (0.0-1.0 as fraction)
                                      For horizontal: fraction of height
                                      For vertical: fraction of width
                                      Default from config
            entrance_line_orientation (str): 'horizontal' or 'vertical'
                                            Default from config
            enable_logging (bool): Whether to log events to CSV file
        
        REALISTIC STORE SETUP:
        ---------------------
        Single entrance/exit door (like real stores!)
        
        HORIZONTAL LINE (door at top/bottom):
        Frame coordinate system:
            (0,0) ----------------------> X (width)
              |
              |   OUTSIDE (street/parking)
              |
              |  ═══════════════  ← Entrance Line (horizontal)
              |       ↓ Entry (downward)
              |       ↑ Exit (upward)
              |   INSIDE (store interior)
              v
              Y (height)
        
        VERTICAL LINE (door at left/right):
        Frame coordinate system:
            (0,0) ----------------------> X (width)
              |     ║                  
              |  O  ║  INSIDE          
              |  U  ║  (store)         
              |  T  ║                  
              |  S  ║  → Entry (rightward)
              |  I  ║  ← Exit (leftward)
              |  D  ║                  
              |  E  ║                  
              v     ║
              Y     Entrance Line (vertical)
        
        Direction Logic:
        HORIZONTAL: Crossing line DOWNWARD (y↑) = ENTRY, UPWARD (y↓) = EXIT
        VERTICAL: Crossing line RIGHTWARD (x↑) = ENTRY, LEFTWARD (x↓) = EXIT
        """
        # Frame dimensions
        self.frame_height = frame_height
        self.frame_width = frame_width
        
        # Line orientation and position
        self.orientation = entrance_line_orientation or ENTRANCE_LINE_ORIENTATION
        self.entrance_line_pos = entrance_line_pos or ENTRANCE_LINE_POSITION
        self.reverse_direction = REVERSE_ENTRY_DIRECTION  # Direction reversal flag
        
        # Calculate pixel coordinate for entrance line
        if self.orientation == 'vertical':
            # Vertical line: position is fraction of WIDTH
            self.entrance_line_x = int(self.entrance_line_pos * frame_width)
            self.entrance_line_y = None  # Not used for vertical
        else:
            # Horizontal line: position is fraction of HEIGHT
            self.entrance_line_y = int(self.entrance_line_pos * frame_height)
            self.entrance_line_x = None  # Not used for horizontal
        
        # Counters
        self.entry_count = 0  # Total unique entries
        self.exit_count = 0   # Total unique exits
        
        # Track history: {track_id: deque([(pos, frame_num), ...])}
        # For horizontal: pos = y_pos
        # For vertical: pos = x_pos
        self.track_history = defaultdict(lambda: deque(maxlen=MIN_FRAMES_FOR_DIRECTION * 2))
        
        # Sets to prevent double counting
        # Once an ID is counted for entry/exit, it's added here
        self.counted_entries = set()
        self.counted_exits = set()
        
        # Currently active tracks (people in frame)
        self.active_tracks = set()
        
        # People currently "inside" the store (between entry and exit lines)
        # This helps track occupancy
        self.people_inside = set()
        
        # Event log for detailed analysis
        # Each event: {'id', 'type', 'timestamp', 'frame', 'position'}
        self.event_log = []
        
        # Logging settings
        self.enable_logging = enable_logging
        self.log_file = REPORTS_DIR / "logs" / FOOTFALL_LOG_FILE
        
        # Statistics
        self.start_time = datetime.now()
        self.frame_count = 0
        
        # Initial occupancy detection flag
        self.initial_occupancy_detected = False
        
        print(f"\n{'='*60}")
        print("FOOTFALL COUNTER INITIALIZED - REALISTIC MODE")
        print(f"{'='*60}")
        print(f"Frame Size: {frame_width}x{frame_height}")
        
        if self.orientation == 'vertical':
            print(f"Entrance Line: X={self.entrance_line_x}px ({self.entrance_line_pos*100:.0f}% from left)")
            if self.reverse_direction:
                print(f"← Cross leftward (from right) = ENTRY (into store)")
                print(f"→ Cross rightward (to right) = EXIT (out of store)")
            else:
                print(f"→ Cross rightward = ENTRY (into store)")
                print(f"← Cross leftward = EXIT (out of store)")
        else:
            print(f"Entrance Line: Y={self.entrance_line_y}px ({self.entrance_line_pos*100:.0f}% from top)")
            if self.reverse_direction:
                print(f"↑ Cross upward = ENTRY (into store)")
                print(f"↓ Cross downward = EXIT (out of store)")
            else:
                print(f"↓ Cross downward = ENTRY (into store)")
                print(f"↑ Cross upward = EXIT (out of store)")
        
        print(f"Logging: {'Enabled' if enable_logging else 'Disabled'}")
        print(f"{'='*60}\n")
    
    
    def _get_center_point(self, bbox):
        """
        Calculate center point of bounding box
        
        Args:
            bbox (tuple): Bounding box (x1, y1, x2, y2)
                         x1, y1 = top-left corner
                         x2, y2 = bottom-right corner
        
        Returns:
            tuple: (center_x, center_y)
        
        MATH EXPLANATION:
        ----------------
        Box corners: (x1, y1) and (x2, y2)
        Center X = (x1 + x2) / 2
        Center Y = (y1 + y2) / 2
        
        Example:
            Box: (100, 200, 150, 300)
            Center: ((100+150)/2, (200+300)/2) = (125, 250)
        
        WHY CENTER POINT?
        ----------------
        - More stable than using corners (which can vary)
        - Represents person's approximate position
        - Less affected by pose changes (arms moving, etc.)
        """
        x1, y1, x2, y2 = bbox
        center_x = int((x1 + x2) / 2)
        center_y = int((y1 + y2) / 2)
        return center_x, center_y
    
    
    def _check_line_crossing(self, track_id, current_pos, frame_num):
        """
        Check if a track crossed the entrance line
        
        This is the CORE ALGORITHM of footfall counting!
        
        REALISTIC STORE LOGIC:
        ---------------------
        Single entrance/exit at same location (like real stores!)
        
        HORIZONTAL LINE (door at top/bottom):
        - Cross DOWNWARD (y↑, into store) = ENTRY
        - Cross UPWARD (y↓, out of store) = EXIT
        
        VERTICAL LINE (door at left/right):
        - Cross RIGHTWARD (x↑, into store) = ENTRY
        - Cross LEFTWARD (x↓, out of store) = EXIT
        
        Args:
            track_id (int): Unique ID of the tracked person
            current_pos (int): Current position (Y for horizontal, X for vertical)
            frame_num (int): Current frame number
        
        Returns:
            tuple: (event_type, direction) or (None, None)
                  event_type: 'entry' or 'exit' or None
                  direction: 'down'/'up' (horizontal) or 'right'/'left' (vertical)
        
        ALGORITHM STEP-BY-STEP:
        ----------------------
        1. Get person's position history (last N frames)
        2. If not enough history, return None (need at least 2 points)
        3. Get previous position and current position
        4. Check if crossed entrance line:
           
           HORIZONTAL:
           - Was above line (prev < line) AND now below (curr >= line)
             → Crossed DOWNWARD → ENTRY ✅
           - Was below line (prev >= line) AND now above (curr < line)
             → Crossed UPWARD → EXIT ✅
           
           VERTICAL:
           - Was left of line (prev < line) AND now right (curr >= line)
             → Crossed RIGHTWARD → ENTRY ✅
           - Was right of line (prev >= line) AND now left (curr < line)
             → Crossed LEFTWARD → EXIT ✅
        
        5. Verify movement with buffer (minimum pixels to confirm crossing)
        """
        # Get history for this track
        history = self.track_history[track_id]
        
        # Need at least 2 points to determine crossing
        if len(history) < 2:
            if FOOTFALL_DEBUG_MODE:
                print(f"[DEBUG] ID:{track_id} | History too short: {len(history)} points")
            return None, None
        
        # Get previous position (second-to-last in history)
        prev_pos, _ = history[-2]
        
        # Calculate direction of movement
        direction_delta = current_pos - prev_pos
        
        # Get line position based on orientation
        if self.orientation == 'vertical':
            line_pos = self.entrance_line_x
            entry_direction = 'right'
            exit_direction = 'left'
            coord_name = 'X'
        else:
            line_pos = self.entrance_line_y
            entry_direction = 'down'
            exit_direction = 'up'
            coord_name = 'Y'
        
        # Debug logging - ENHANCED
        if FOOTFALL_DEBUG_MODE:
            side_prev = "LEFT" if prev_pos < line_pos else "RIGHT"
            side_curr = "LEFT" if current_pos < line_pos else "RIGHT"
            print(f"[DEBUG] ID:{track_id} | {coord_name}: {prev_pos:.0f} ({side_prev}) → {current_pos:.0f} ({side_curr}) | Line: {line_pos:.0f} | Delta: {direction_delta:.0f}")
        
        # Apply direction reversal if configured
        if self.reverse_direction:
            # Swap entry and exit directions
            entry_direction, exit_direction = exit_direction, entry_direction
        
        # Check if line was crossed (person moved from one side to the other)
        # FIXED: Use bidirectional crossing detection with buffer zone
        crossed_line = False
        crossing_direction = None
        
        # CASE 1: Crossed from LEFT to RIGHT (or TOP to BOTTOM)
        # Person was on left/top side, now on right/bottom side
        if prev_pos < line_pos and current_pos > line_pos:
            if abs(direction_delta) > CROSSING_BUFFER:
                crossed_line = True
                crossing_direction = 'positive'  # Positive direction (right/down)
                if FOOTFALL_DEBUG_MODE:
                    print(f"  → CROSSED! Direction: LEFT→RIGHT (positive)")
        
        # CASE 2: Crossed from RIGHT to LEFT (or BOTTOM to TOP)
        # Person was on right/bottom side, now on left/top side
        elif prev_pos > line_pos and current_pos < line_pos:
            if abs(direction_delta) > CROSSING_BUFFER:
                crossed_line = True
                crossing_direction = 'negative'  # Negative direction (left/up)
                if FOOTFALL_DEBUG_MODE:
                    print(f"  → CROSSED! Direction: RIGHT→LEFT (negative)")
        
        # Determine if it's entry or exit based on direction
        if crossed_line:
            if crossing_direction == 'positive':
                # Positive direction crossing (left→right or top→bottom)
                if self.reverse_direction:
                    result = ('exit', exit_direction)
                    if FOOTFALL_DEBUG_MODE:
                        print(f"  ✅ Result: EXIT (reversed mode)")
                    return result
                else:
                    result = ('entry', entry_direction)
                    if FOOTFALL_DEBUG_MODE:
                        print(f"  ✅ Result: ENTRY (normal mode)")
                    return result
            
            elif crossing_direction == 'negative':
                # Negative direction crossing (right→left or bottom→top)
                if self.reverse_direction:
                    result = ('entry', entry_direction)
                    if FOOTFALL_DEBUG_MODE:
                        print(f"  ✅ Result: ENTRY (reversed mode)")
                    return result
                else:
                    result = ('exit', exit_direction)
                    if FOOTFALL_DEBUG_MODE:
                        print(f"  ✅ Result: EXIT (normal mode)")
                    return result
        
        return None, None
    
    
    def _log_event(self, track_id, event_type, frame_num, position):
        """
        Log an entry/exit event
        
        Args:
            track_id (int): ID of the person
            event_type (str): 'entry' or 'exit'
            frame_num (int): Frame number when event occurred
            position (tuple): (x, y) position where crossing happened
        
        This creates a detailed record for later analysis:
        - When did person enter/exit?
        - What was their ID?
        - Where exactly did they cross?
        
        BUSINESS VALUE:
        ---------------
        This log enables:
        - Hourly/daily/weekly footfall reports
        - Peak hour identification
        - Average dwell time calculation
        - Conversion rate analysis
        """
        event = {
            'track_id': track_id,
            'event_type': event_type,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'frame': frame_num,
            'position_x': position[0],
            'position_y': position[1]
        }
        
        self.event_log.append(event)
        
        # Print real-time event notification
        emoji = "🟢" if event_type == 'entry' else "🔴"
        print(f"{emoji} {event_type.upper()}: ID {track_id} | Frame {frame_num} | Time {event['timestamp']}")
    
    
    def update(self, tracked_objects, frame_num):
        """
        Update footfall counter with new tracked objects
        
        This is called ONCE PER FRAME to analyze all tracked persons.
        
        Args:
            tracked_objects (list): List of tracked objects from PersonTracker
                Each object has: {'id', 'bbox', 'center', ...}
            frame_num (int): Current frame number
        
        Returns:
            dict: Current statistics {'entries', 'exits', 'occupancy'}
        
        PROCESSING FLOW:
        ---------------
        1. Update frame count
        2. Clear active tracks (will repopulate with current frame)
        3. For each tracked person:
           a. Extract ID and bounding box
           b. Calculate center point
           c. Add to track history
           d. Check for line crossing
           e. If crossed, update counters and log event
        4. Update occupancy
        5. Return current stats
        
        EXAMPLE USAGE:
        -------------
        ```python
        frame_num = 0
        for frame in video:
            detections = detector.detect(frame)
            tracked = tracker.update(detections)
            stats = counter.update(tracked, frame_num)
            
            print(f"Entries: {stats['entries']}, Exits: {stats['exits']}")
            frame_num += 1
        """
        self.frame_count = frame_num
        self.active_tracks.clear()
        
        # INITIAL OCCUPANCY DETECTION
        # On first frame, count people already inside store region as entries
        if not self.initial_occupancy_detected and frame_num <= 10:
            initial_inside = []
            
            for obj in tracked_objects:
                track_id = obj['id']
                bbox = obj['bbox']
                cx, cy = self._get_center_point(bbox)
                
                # Check if person is on the "inside" side of the line
                if self.orientation == 'vertical':
                    pos = cx
                    line_pos = self.entrance_line_x
                    # For vertical with reverse: inside = right side (pos > line)
                    # For vertical without reverse: inside = right side (pos > line)
                    if self.reverse_direction:
                        # Reverse: entry from right (leftward), so inside = left side
                        is_inside = pos < line_pos
                    else:
                        # Normal: entry from left (rightward), so inside = right side
                        is_inside = pos > line_pos
                else:
                    pos = cy
                    line_pos = self.entrance_line_y
                    # For horizontal with reverse: inside = top side (pos < line)
                    # For horizontal without reverse: inside = bottom side (pos > line)
                    if self.reverse_direction:
                        is_inside = pos < line_pos
                    else:
                        is_inside = pos > line_pos
                
                if is_inside:
                    initial_inside.append((track_id, cx, cy))
            
            # Count initial people as entries
            if initial_inside and frame_num >= 5:  # Wait a few frames for stable tracking
                self.initial_occupancy_detected = True
                print(f"\n🔵 INITIAL OCCUPANCY DETECTED: {len(initial_inside)} people already inside store")
                
                for track_id, cx, cy in initial_inside:
                    if track_id not in self.counted_entries:
                        self.entry_count += 1
                        self.counted_entries.add(track_id)
                        self.people_inside.add(track_id)
                        self._log_event(track_id, 'entry', frame_num, (cx, cy))
                        print(f"  ↳ ID {track_id} counted as initial entry")
                
                print(f"✅ Initial entries: {self.entry_count}\n")
        
        for obj in tracked_objects:
            track_id = obj['id']
            bbox = obj['bbox']
            
            # Mark as active
            self.active_tracks.add(track_id)
            
            # Get center point
            cx, cy = self._get_center_point(bbox)
            
            # Get position based on orientation
            if self.orientation == 'vertical':
                pos = cx  # Use X position for vertical line
            else:
                pos = cy  # Use Y position for horizontal line
            
            # Debug: Show track info
            if FOOTFALL_DEBUG_MODE and frame_num % 10 == 0:  # Every 10 frames
                print(f"[TRACK] ID:{track_id} | Center: ({cx:.0f}, {cy:.0f}) | Pos: {pos:.0f}")
            
            # Add to history
            self.track_history[track_id].append((pos, frame_num))
            
            # Check for line crossing
            crossed_line, direction = self._check_line_crossing(track_id, pos, frame_num)
            
            if crossed_line == 'entry' and track_id not in self.counted_entries:
                # NEW ENTRY!
                self.entry_count += 1
                self.counted_entries.add(track_id)
                self.people_inside.add(track_id)
                self._log_event(track_id, 'entry', frame_num, (cx, cy))
                
            elif crossed_line == 'exit' and track_id not in self.counted_exits:
                # NEW EXIT!
                self.exit_count += 1
                self.counted_exits.add(track_id)
                # Remove from inside if they were there
                self.people_inside.discard(track_id)
                self._log_event(track_id, 'exit', frame_num, (cx, cy))
        
        # Calculate current occupancy
        # Occupancy = people who entered but haven't exited
        current_occupancy = len(self.people_inside)
        
        return {
            'entries': self.entry_count,
            'exits': self.exit_count,
            'occupancy': current_occupancy
        }
    
    
    def draw_lines(self, frame):
        """
        Draw entrance line on the frame
        
        Args:
            frame (numpy.ndarray): Video frame to draw on
        
        Returns:
            numpy.ndarray: Frame with entrance line drawn
        
        VISUAL DESIGN:
        -------------
        - Single entrance line: YELLOW/CYAN (entrance/exit)
        - Bidirectional arrows showing entry/exit
        - Labels for direction
        - Supports both horizontal and vertical orientations
        """
        if self.orientation == 'vertical':
            # VERTICAL LINE (door on left/right side)
            cv2.line(
                frame,
                (self.entrance_line_x, 0),
                (self.entrance_line_x, self.frame_height),
                LINE_COLOR_ENTRANCE,
                LINE_THICKNESS
            )
            
            # Determine labels based on reverse flag
            if self.reverse_direction:
                # Reversed: Entry from RIGHT (leftward), Exit to RIGHT (rightward)
                left_label = "STORE"
                left_direction = "← Exit"
                right_label = "OUT"
                right_direction = "← Entry"
            else:
                # Normal: Entry from LEFT (rightward), Exit to LEFT (leftward)
                left_label = "OUT"
                left_direction = "→ Entry"
                right_label = "STORE"
                right_direction = "← Exit"
            
            # Label on left side
            cv2.putText(
                frame,
                left_label,
                (self.entrance_line_x - 60, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                LINE_COLOR_ENTRANCE,
                2
            )
            cv2.putText(
                frame,
                left_direction,
                (self.entrance_line_x - 80, 60),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                LINE_COLOR_ENTRANCE,
                2
            )
            
            # Label on right side
            cv2.putText(
                frame,
                right_label,
                (self.entrance_line_x + 10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                LINE_COLOR_ENTRANCE,
                2
            )
            cv2.putText(
                frame,
                right_direction,
                (self.entrance_line_x + 10, 60),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                LINE_COLOR_ENTRANCE,
                2
            )
            
        else:
            # HORIZONTAL LINE (door at top/bottom)
            cv2.line(
                frame,
                (0, self.entrance_line_y),
                (self.frame_width, self.entrance_line_y),
                LINE_COLOR_ENTRANCE,
                LINE_THICKNESS
            )
            
            # Determine labels based on reverse flag
            if self.reverse_direction:
                # Reversed: Entry from BOTTOM (upward), Exit to BOTTOM (downward)
                top_label = "ENTRANCE ↑ Entry"
                bottom_label = "↓ Exit"
            else:
                # Normal: Entry from TOP (downward), Exit to TOP (upward)
                top_label = "ENTRANCE ↓ Entry"
                bottom_label = "↑ Exit"
            
            # Add label above line
            cv2.putText(
                frame,
                top_label,
                (10, self.entrance_line_y - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                LINE_COLOR_ENTRANCE,
                2
            )
            
            # Add label below line
            cv2.putText(
                frame,
                bottom_label,
                (10, self.entrance_line_y + 25),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                LINE_COLOR_ENTRANCE,
                2
            )
        
        return frame
    
    
    def draw_stats(self, frame, position='top-right'):
        """
        Draw footfall statistics on the frame
        
        Args:
            frame (numpy.ndarray): Video frame
            position (str): Where to draw stats ('top-left', 'top-right', etc.)
        
        Returns:
            numpy.ndarray: Frame with statistics overlay
        
        DISPLAY LAYOUT:
        --------------
        ┌─────────────────────┐
        │ 📊 FOOTFALL STATS   │
        │ ➜ Entries: 45       │
        │ ⬅ Exits: 42         │
        │ 👥 Occupancy: 3     │
        │ ⏱ Time: 01:23:45    │
        └─────────────────────┘
        """
        # Calculate position based on parameter
        if position == 'top-right':
            x = self.frame_width - 300
            y = 30
        else:  # top-left
            x = 10
            y = 30
        
        # Semi-transparent background
        overlay = frame.copy()
        cv2.rectangle(
            overlay,
            (x - 10, y - 10),
            (x + 280, y + 140),
            (0, 0, 0),
            -1
        )
        frame = cv2.addWeighted(overlay, 0.6, frame, 0.4, 0)
        
        # Draw title
        cv2.putText(
            frame,
            "FOOTFALL STATISTICS",
            (x, y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2
        )
        
        # Draw entries
        cv2.putText(
            frame,
            f"Entries:   {self.entry_count}",
            (x, y + 35),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (0, 255, 0),  # Green
            2
        )
        
        # Draw exits
        cv2.putText(
            frame,
            f"Exits:     {self.exit_count}",
            (x, y + 65),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (0, 0, 255),  # Red
            2
        )
        
        # Draw current occupancy
        occupancy = len(self.people_inside)
        cv2.putText(
            frame,
            f"Occupancy: {occupancy}",
            (x, y + 95),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (0, 255, 255),  # Yellow
            2
        )
        
        # Draw total unique visitors
        total_visitors = len(self.counted_entries)
        cv2.putText(
            frame,
            f"Visitors:  {total_visitors}",
            (x, y + 125),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 165, 0),  # Orange
            2
        )
        
        # Draw elapsed time
        elapsed = datetime.now() - self.start_time
        time_str = str(elapsed).split('.')[0]  # Remove microseconds
        cv2.putText(
            frame,
            f"Time: {time_str}",
            (x, y + 155),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (200, 200, 200),
            1
        )
        
        return frame
    
    
    def get_statistics(self):
        """
        Get comprehensive statistics
        
        Returns:
            dict: Complete statistics dictionary
        
        METRICS INCLUDED:
        ----------------
        - Basic counts (entries, exits, occupancy)
        - Time-based metrics (duration, rate)
        - Conversion metrics (if sales data available)
        
        USE CASES:
        ---------
        - End of day reporting
        - Real-time dashboard updates
        - Historical trend analysis
        """
        elapsed = datetime.now() - self.start_time
        elapsed_seconds = elapsed.total_seconds()
        
        # Calculate rates (per hour)
        hours = elapsed_seconds / 3600 if elapsed_seconds > 0 else 1
        entry_rate = self.entry_count / hours
        exit_rate = self.exit_count / hours
        
        stats = {
            'entries': self.entry_count,
            'exits': self.exit_count,
            'current_occupancy': len(self.people_inside),
            'total_unique_visitors': len(self.counted_entries),
            'elapsed_time': str(elapsed).split('.')[0],
            'elapsed_seconds': int(elapsed_seconds),
            'entry_rate_per_hour': round(entry_rate, 2),
            'exit_rate_per_hour': round(exit_rate, 2),
            'total_frames': self.frame_count,
            'unique_tracks': len(self.track_history),
            'event_count': len(self.event_log)
        }
        
        return stats
    
    
    def save_log(self, filename=None):
        """
        Save event log to CSV file
        
        Args:
            filename (str): Optional custom filename
        
        This creates a permanent record of all entry/exit events for:
        - Historical analysis
        - Business intelligence
        - Auditing and verification
        
        CSV FORMAT:
        ----------
        track_id,event_type,timestamp,frame,position_x,position_y
        0,entry,2024-01-22 10:05:32,150,640,216
        1,entry,2024-01-22 10:05:45,450,580,216
        0,exit,2024-01-22 10:12:18,12450,660,504
        """
        if not self.enable_logging:
            print("⚠️  Logging is disabled. Enable in config to save logs.")
            return
        
        if not self.event_log:
            print("ℹ️  No events to log.")
            return
        
        # Use custom filename or default
        log_path = filename or self.log_file
        
        # Ensure directory exists
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write CSV
        with open(log_path, 'w', newline='') as f:
            fieldnames = ['track_id', 'event_type', 'timestamp', 'frame', 
                         'position_x', 'position_y']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            
            writer.writeheader()
            for event in self.event_log:
                writer.writerow(event)
        
        print(f"\n✅ Footfall log saved: {log_path}")
        print(f"   Total events: {len(self.event_log)}")
    
    
    def reset(self):
        """
        Reset all counters and logs
        
        Useful for:
        - Starting a new counting session
        - Testing different parameters
        - Clearing data between video files
        """
        self.entry_count = 0
        self.exit_count = 0
        self.track_history.clear()
        self.counted_entries.clear()
        self.counted_exits.clear()
        self.active_tracks.clear()
        self.people_inside.clear()
        self.event_log.clear()
        self.start_time = datetime.now()
        self.frame_count = 0
        
        print("🔄 Footfall counter reset")
    
    
    def print_summary(self):
        """
        Print a formatted summary of statistics
        
        Provides a quick overview of the counting session.
        """
        stats = self.get_statistics()
        
        print(f"\n{'='*60}")
        print("FOOTFALL COUNTING SUMMARY")
        print(f"{'='*60}")
        print(f"📥 Total Entries:       {stats['entries']}")
        print(f"📤 Total Exits:         {stats['exits']}")
        print(f"👥 Current Occupancy:   {stats['current_occupancy']}")
        print(f"⏱  Duration:            {stats['elapsed_time']}")
        print(f"📊 Entry Rate:          {stats['entry_rate_per_hour']:.1f} per hour")
        print(f"📊 Exit Rate:           {stats['exit_rate_per_hour']:.1f} per hour")
        print(f"🎬 Total Frames:        {stats['total_frames']}")
        print(f"🔢 Unique Tracks:       {stats['unique_tracks']}")
        print(f"📋 Events Logged:       {stats['event_count']}")
        print(f"{'='*60}\n")


# ==================== TESTING FUNCTION ====================
def test_footfall_counter():
    """
    Test the footfall counter with webcam
    
    This function demonstrates Phase 4 capabilities:
    - Detection (Phase 2)
    - Tracking (Phase 3)
    - Footfall Counting (Phase 4) ← NEW!
    
    Controls:
    - 'q': Quit
    - 't': Toggle tracking
    - 'r': Reset counters
    - 's': Save snapshot
    """
    print("\n" + "="*60)
    print("PHASE 4 TEST: FOOTFALL COUNTER WITH WEBCAM")
    print("="*60)
    print("Controls:")
    print("  'q' - Quit")
    print("  't' - Toggle tracking")
    print("  'r' - Reset counters")
    print("  's' - Save snapshot")
    print("="*60 + "\n")
    
    # Import required modules
    from src.detection.person_detector import PersonDetector
    from src.tracking.tracker import PersonTracker
    from src.utils.video_handler import VideoHandler
    
    # Initialize components
    print("Initializing system...")
    detector = PersonDetector()
    tracker = PersonTracker(max_age=30, min_hits=3, iou_threshold=0.3)
    video_handler = VideoHandler(source=0)  # Webcam
    
    # Get frame dimensions
    ret, frame = video_handler.read_frame()
    if not ret:
        print("❌ Failed to read from webcam")
        return
    
    height, width = frame.shape[:2]
    
    # Initialize footfall counter (realistic: single entrance/exit)
    counter = FootfallCounter(
        frame_height=height,
        frame_width=width,
        entrance_line_pos=0.5  # 50% from top (realistic entrance position)
    )
    
    # Colors for visualization
    colors = [
        (255, 0, 0), (0, 255, 0), (0, 0, 255),
        (255, 255, 0), (255, 0, 255), (0, 255, 255),
        (128, 0, 128), (255, 165, 0), (0, 128, 128)
    ]
    
    tracking_enabled = True
    frame_num = 0
    
    print("✅ System ready! Press 'q' to quit.\n")
    
    try:
        while True:
            ret, frame = video_handler.read_frame()
            if not ret:
                break
            
            # Detect persons
            detections = detector.detect(frame, visualize=False)
            
            if tracking_enabled:
                # Track persons
                tracked_objects = tracker.update(detections)
                
                # Update footfall counter
                stats = counter.update(tracked_objects, frame_num)
                
                # Draw tracked boxes with IDs
                for obj in tracked_objects:
                    track_id = obj['id']
                    bbox = obj['bbox']
                    x1, y1, x2, y2 = map(int, bbox)
                    
                    # Color based on ID
                    color = colors[track_id % len(colors)]
                    
                    # Draw box
                    cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                    
                    # Draw ID
                    label = f"ID: {track_id}"
                    cv2.putText(frame, label, (x1, y1 - 10),
                              cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
                    
                    # Draw center point
                    cx, cy = counter._get_center_point(bbox)
                    cv2.circle(frame, (cx, cy), 5, color, -1)
            else:
                # Just show detections
                for det in detections:
                    bbox = det['bbox']
                    conf = det['confidence']
                    x1, y1, x2, y2 = map(int, bbox)
                    
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    cv2.putText(frame, f"{conf:.2f}", (x1, y1 - 10),
                              cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            
            # Draw footfall lines and stats
            frame = counter.draw_lines(frame)
            frame = counter.draw_stats(frame)
            
            # Display
            cv2.imshow('Phase 4: Footfall Counter', frame)
            
            # Handle keyboard input
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('t'):
                tracking_enabled = not tracking_enabled
                print(f"🔄 Tracking {'enabled' if tracking_enabled else 'disabled'}")
            elif key == ord('r'):
                counter.reset()
                tracker = PersonTracker(max_age=30, min_hits=3, iou_threshold=0.3)
            elif key == ord('s'):
                snapshot_path = f"footfall_snapshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
                cv2.imwrite(snapshot_path, frame)
                print(f"📸 Snapshot saved: {snapshot_path}")
            
            frame_num += 1
    
    finally:
        # Cleanup and print summary
        video_handler.release()
        cv2.destroyAllWindows()
        
        counter.print_summary()
        counter.save_log()


if __name__ == "__main__":
    test_footfall_counter()
