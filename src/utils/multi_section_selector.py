"""
Multi-Section Selector Utility

Interactive UI for defining multiple sections/zones in the store.
Allows users to define as many sections as needed (Electronics, Clothing, etc.).

Author: Smart Retail Analytics Team
Phase: 5 - Advanced Analytics
"""

import cv2
import numpy as np
import json
from pathlib import Path
import sys

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))
from config import *


class MultiSectionSelector:
    """
    Interactive tool for defining multiple store sections.
    
    Simplified approach:
    - Prompt for section name in console
    - Open window to click boundary points
    - Right-click to complete section
    - Repeat for next section
    - Type 'q' when all sections defined
    """
    
    def __init__(self, frame):
        """
        Initialize the Multi-Section Selector.
        
        Args:
            frame: First frame of video to draw on
        """
        self.original_frame = frame.copy()
    
    def select_sections(self):
        """
        Main function to select multiple sections interactively.
        
        Returns:
            list: List of section dictionaries, or None if cancelled
        """
        sections = []
        
        print("\n" + "="*60)
        print("SECTION SELECTION - Define Store Sections")
        print("="*60)
        print("📍 You'll define multiple sections (e.g., Electronics, Clothing)")
        print("\nFor EACH section:")
        print("  1. Enter section name in console")
        print("  2. Window opens - Left-click to add boundary points")
        print("  3. Right-click to complete section")
        print("  4. Repeat for next section")
        print("\nWhen done:")
        print("  - Type 'q' to finish defining sections")
        print("="*60 + "\n")
        
        section_num = 1
        
        while True:
            # Prompt for section name
            print("-" * 60)
            section_name = input(f"📍 Section {section_num} - Enter name (or 'q' to finish): ").strip()
            print("-" * 60)
            
            if section_name.lower() == 'q':
                if len(sections) == 0:
                    print("⚠️  No sections defined! You must define at least 1 section.")
                    print("   Please enter a section name or press Ctrl+C to cancel.\n")
                    continue
                break
            
            if not section_name:
                print("⚠️  Section name cannot be empty! Try again.\n")
                continue
            
            # Define boundary for this section
            print(f"\n🖼️  Opening window to define '{section_name}' boundary...")
            print("   👉 Left-click to add points")
            print("   👉 Right-click when done (minimum 3 points)\n")
            
            points = self._select_zone_for_section(section_name)
            
            if points and len(points) >= 3:
                sections.append({
                    'name': section_name,
                    'points': points
                })
                print(f"\n✅ Section '{section_name}' saved with {len(points)} points!")
                print(f"   Total sections defined so far: {len(sections)}\n")
                section_num += 1
            else:
                print(f"\n❌ Section '{section_name}' cancelled or invalid (need 3+ points)\n")
        
        if len(sections) > 0:
            print("\n" + "="*60)
            print(f"✅ SECTION DEFINITION COMPLETE - {len(sections)} sections defined:")
            for idx, section in enumerate(sections, 1):
                print(f"   {idx}. {section['name']} ({len(section['points'])} points)")
            print("="*60 + "\n")
        
        return sections if len(sections) > 0 else None
    
    def _select_zone_for_section(self, section_name):
        """
        Open window for user to click points defining a section boundary.
        
        Args:
            section_name: Name of the section being defined
        
        Returns:
            list: List of (x, y) tuples, or None if cancelled
        """
        points = []
        window_name = f"Define: {section_name}"
        section_complete = False
        
        def mouse_callback(event, x, y, flags, param):
            nonlocal points, section_complete
            
            if event == cv2.EVENT_LBUTTONDOWN:
                # Add point
                points.append((x, y))
                print(f"   ✓ Point {len(points)} added: ({x}, {y})")
            
            elif event == cv2.EVENT_RBUTTONDOWN:
                # Complete section
                if len(points) >= 3:
                    section_complete = True
                    print(f"\n   ✅ Section complete with {len(points)} points!")
                    print("   🔄 Closing window...\n")
                else:
                    print(f"   ⚠️  Need at least 3 points! Currently: {len(points)}")
        
        # Create window
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(window_name, 1280, 720)
        cv2.setMouseCallback(window_name, mouse_callback)
        
        # Main loop
        while not section_complete:
            # Draw frame with points
            display_frame = self.original_frame.copy()
            
            # Draw all points
            for i, point in enumerate(points):
                cv2.circle(display_frame, point, 5, (0, 255, 0), -1)
                cv2.putText(display_frame, str(i + 1), 
                           (point[0] + 10, point[1] - 10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            
            # Draw lines connecting points
            if len(points) > 1:
                for i in range(len(points) - 1):
                    cv2.line(display_frame, points[i], points[i + 1], 
                            (0, 255, 255), 2)
            
            # Draw closing line preview
            if len(points) > 2:
                cv2.line(display_frame, points[-1], points[0], 
                        (0, 255, 255), 1, cv2.LINE_AA)
            
            # Add instructions overlay
            cv2.putText(display_frame, f"Section: {section_name}", 
                       (10, 35),
                       cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 3)
            cv2.putText(display_frame, f"Section: {section_name}", 
                       (10, 35),
                       cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 255), 2)
            
            cv2.putText(display_frame, f"Points: {len(points)}", 
                       (10, 75),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
            
            instructions = [
                "Left-click: Add point",
                "Right-click: Complete (min 3 points)",
                "Q: Cancel"
            ]
            
            y_pos = display_frame.shape[0] - 80
            for instruction in instructions:
                cv2.putText(display_frame, instruction, 
                           (10, y_pos),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
                y_pos += 25
            
            cv2.imshow(window_name, display_frame)
            
            # Handle keyboard
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q') or key == 27:  # Q or ESC
                print(f"   ❌ Section '{section_name}' cancelled by user")
                cv2.destroyAllWindows()
                cv2.waitKey(100)
                return None
            
            # Check if window was closed
            if cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE) < 1:
                break
        
        # Clean up
        cv2.destroyAllWindows()
        cv2.waitKey(100)  # Allow window to fully close
        
        return points if len(points) >= 3 else None
    
    @staticmethod
    def save_sections(sections, video_path):
        """
        Save sections to JSON file.
        
        Args:
            sections: List of section dictionaries
            video_path: Path to video file (used for filename)
        """
        sections_dir = Path("sections")
        sections_dir.mkdir(exist_ok=True)
        
        video_name = Path(video_path).stem
        json_path = sections_dir / f"{video_name}_sections.json"
        
        # Prepare data (remove color if present for JSON serialization)
        save_data = []
        for section in sections:
            save_data.append({
                'name': section['name'],
                'points': section['points']
            })
        
        data = {
            'video': str(video_path),
            'sections': save_data,
            'num_sections': len(save_data)
        }
        
        with open(json_path, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"💾 Sections saved: {json_path}")
    
    @staticmethod
    def load_sections(video_path):
        """
        Load sections from JSON file.
        
        Args:
            video_path: Path to video file
        
        Returns:
            list: List of section dictionaries, or None if not found
        """
        sections_dir = Path("sections")
        video_name = Path(video_path).stem
        json_path = sections_dir / f"{video_name}_sections.json"
        
        if not json_path.exists():
            return None
        
        try:
            with open(json_path, 'r') as f:
                data = json.load(f)
            
            sections = data['sections']
            print(f"📂 Loaded {len(sections)} sections from {json_path}")
            return sections
        
        except Exception as e:
            print(f"❌ Error loading sections: {e}")
            return None
