"""
Main script for Smart Retail Analytics System

This is the entry point for running the system.

Usage:
    python main.py --webcam              # Test with webcam
    python main.py --video path.mp4      # Process video file
    python main.py --demo                # Run demo mode
"""

import argparse
import sys
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

from config import *
from detection.person_detector import PersonDetector
from tracking.tracker import PersonTracker
from analytics.footfall_counter import FootfallCounter  # OLD: Phase 4 (line-based)
from analytics.occupancy_tracker import OccupancyTracker  # NEW: Phase 4 (zone-based)
from utils.video_handler import VideoHandler, VideoWriter
from utils.zone_selector import ZoneSelector
import cv2


def run_footfall_demo():
    """Run real-time footfall counting on webcam (Phase 4)."""
    print("\n" + "="*60)
    print("SMART RETAIL ANALYTICS - PHASE 4: FOOTFALL COUNTING")
    print("="*60)
    print("Controls:")
    print("  'q' - Quit and show summary")
    print("  's' - Save snapshot")
    print("  'r' - Reset counters")
    print("  't' - Toggle tracking ON/OFF")
    print("="*60 + "\n")
    
    # Initialize
    detector = PersonDetector()
    tracker = PersonTracker(max_age=30, min_hits=3, iou_threshold=0.3)
    video = VideoHandler(use_webcam=True)
    
    # Get frame dimensions
    ret, frame = video.read_frame()
    if not ret:
        print("❌ Failed to read from webcam")
        return
    
    height, width = frame.shape[:2]
    
    # Setup proper display window (fixes small window in corner issue)
    window_name = VideoHandler.setup_window(
        window_name="Phase 4: Footfall Counting",
        width=1280,
        height=720,
        x=50,
        y=50
    )
    
    # Initialize footfall counter (realistic: single entrance/exit)
    # Position and orientation are read from config.py
    counter = FootfallCounter(
        frame_height=height,
        frame_width=width
    )
    
    # Add mouse callback for debugging coordinates
    VideoHandler.add_mouse_callback(
        window_name=window_name,
        frame_width=width,
        frame_height=height,
        entrance_line_pos=ENTRANCE_LINE_POSITION
    )
    
    # Print debug info
    print(f"\n{'='*60}")
    print("🔍 COORDINATE DEBUG INFO")
    print(f"{'='*60}")
    print(f"Frame size: {width}x{height}")
    print(f"Entrance line at: X={int(width * ENTRANCE_LINE_POSITION)} ({ENTRANCE_LINE_POSITION*100:.0f}% from left)")
    print(f"Line orientation: {ENTRANCE_LINE_ORIENTATION}")
    print(f"Direction reversed: {REVERSE_ENTRY_DIRECTION}")
    print(f"\n👆 TIP: Click anywhere on the frame to see pixel coordinates!")
    print(f"{'='*60}\n")
    
    # Colors for visualization
    colors = [
        (255, 0, 0), (0, 255, 0), (0, 0, 255),
        (255, 255, 0), (255, 0, 255), (0, 255, 255),
        (128, 0, 128), (255, 165, 0), (0, 128, 128)
    ]
    
    tracking_enabled = True
    frame_count = 0
    
    print("✅ System ready! Walk across the entry/exit lines to test.\n")
    
    try:
        while True:
            ret, frame = video.read_frame()
            if not ret:
                break
            
            # Detect persons
            detections, _ = detector.detect(frame)
            
            if tracking_enabled:
                # Track persons
                tracked_objects = tracker.update(detections)
                
                # Update footfall counter
                stats = counter.update(tracked_objects, frame_count)
                
                # Draw tracked boxes with IDs
                for obj in tracked_objects:
                    x, y, w, h = [int(v) for v in obj['bbox']]
                    track_id = obj['id']
                    color = colors[track_id % len(colors)]
                    
                    # Draw box
                    cv2.rectangle(frame, (x, y), (x + w, y + h), color, 3)
                    
                    # Draw ID label
                    label = f"ID:{track_id}"
                    cv2.rectangle(frame, (x, y - 30), (x + 80, y), color, -1)
                    cv2.putText(frame, label, (x + 5, y - 8),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                    
                    # Draw center point
                    cx, cy = obj['center']
                    cv2.circle(frame, (cx, cy), 5, color, -1)
            else:
                # Just show detections
                for det in detections:
                    x, y, w, h = det['bbox']
                    x, y, w, h = int(x), int(y), int(w), int(h)
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            
            # Draw footfall lines and statistics
            frame = counter.draw_lines(frame)
            frame = counter.draw_stats(frame, position='top-right')
            
            # Display in properly configured window
            cv2.imshow(window_name, frame)
            
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
                from datetime import datetime
                snapshot_path = f"footfall_snapshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
                cv2.imwrite(snapshot_path, frame)
                print(f"📸 Snapshot saved: {snapshot_path}")
            
            frame_count += 1
    
    finally:
        video.release()
        cv2.destroyAllWindows()
        
        # Print summary and save log
        counter.print_summary()
        counter.save_log()


def run_footfall_video(video_path):
    """Process a video file with footfall counting (Phase 4)."""
    print("\n" + "="*60)
    print("PHASE 4: FOOTFALL COUNTING - VIDEO ANALYSIS")
    print("="*60)
    print(f"Input: {video_path}")
    print("="*60 + "\n")
    
    video_path = Path(video_path)
    
    if not video_path.exists():
        print(f"❌ Video file not found: {video_path}")
        return
    
    # Initialize
    detector = PersonDetector()
    tracker = PersonTracker(max_age=30, min_hits=3, iou_threshold=0.3)
    video = VideoHandler(source=video_path)
    
    # Initialize footfall counter with video dimensions (realistic: single entrance/exit)
    # Position and orientation are read from config.py
    counter = FootfallCounter(
        frame_height=video.frame_height,
        frame_width=video.frame_width
    )
    
    # Output
    output_path = PROCESSED_VIDEOS_DIR / f"footfall_{video_path.name}"
    writer = VideoWriter(output_path, video.fps, video.frame_width, video.frame_height)
    
    # Colors for track IDs
    colors = [
        (255, 0, 0), (0, 255, 0), (0, 0, 255),
        (255, 255, 0), (255, 0, 255), (0, 255, 255),
        (128, 0, 0), (0, 128, 0), (0, 0, 128)
    ]
    
    frame_count = 0
    
    try:
        print("🎬 Processing video with footfall counting...\n")
        
        while True:
            ret, frame = video.read_frame()
            if not ret:
                break
            
            frame_count += 1
            
            # Detect people
            detections, _ = detector.detect(frame)
            
            # Track people
            tracked_objects = tracker.update(detections)
            
            # Update footfall counter
            stats = counter.update(tracked_objects, frame_count)
            
            # Draw tracked objects
            for obj in tracked_objects:
                x, y, w, h = [int(v) for v in obj['bbox']]
                track_id = obj['id']
                color = colors[track_id % len(colors)]
                
                # Draw box
                cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
                
                # Draw ID
                label = f"ID:{track_id}"
                cv2.rectangle(frame, (x, y - 25), (x + 70, y), color, -1)
                cv2.putText(frame, label, (x + 5, y - 7),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                
                # Draw center
                cx, cy = obj['center']
                cv2.circle(frame, (cx, cy), 4, color, -1)
            
            # Draw footfall lines and stats
            frame = counter.draw_lines(frame)
            frame = counter.draw_stats(frame)
            
            # Write frame
            writer.write_frame(frame)
            
            # Progress
            if frame_count % 30 == 0:
                print(f"Processed {frame_count} frames | Entries: {stats['entries']} | Exits: {stats['exits']} | Occupancy: {stats['occupancy']}")
        
        print(f"\n✅ Processing complete!")
        print(f"📹 Saved to: {output_path}")
        
    finally:
        video.release()
        writer.release()
        
        # Print summary and save log
        counter.print_summary()
        counter.save_log()


def run_webcam_demo():
    """Run real-time detection on webcam."""
    print("\n" + "="*60)
    print("SMART RETAIL ANALYTICS - WEBCAM MODE")
    print("="*60)
    print("Press 'q' to quit | Press 's' to save frame")
    print("Press 't' to toggle tracking ON/OFF")
    print("="*60 + "\n")
    
    # Initialize
    detector = PersonDetector()
    tracker = PersonTracker()  # NEW: Add tracker
    video = VideoHandler(use_webcam=True)
    
    # Colors for different track IDs
    colors = [
        (255, 0, 0), (0, 255, 0), (0, 0, 255),
        (255, 255, 0), (255, 0, 255), (0, 255, 255),
        (128, 0, 0), (0, 128, 0), (0, 0, 128)
    ]
    
    frame_count = 0
    use_tracking = True  # Toggle tracking on/off
    
    try:
        while True:
            ret, frame = video.read_frame()
            if not ret:
                break
            
            frame_count += 1
            
            # Detect people
            detections, _ = detector.detect(frame)
            
            if use_tracking:
                # Track people
                tracked_objects = tracker.update(detections)
                
                # Draw tracked objects with IDs
                for obj in tracked_objects:
                    x, y, w, h = [int(v) for v in obj['bbox']]
                    track_id = obj['id']
                    color = colors[track_id % len(colors)]
                    
                    # Draw box
                    cv2.rectangle(frame, (x, y), (x + w, y + h), color, 3)
                    
                    # Draw ID label
                    label = f"ID:{track_id}"
                    cv2.rectangle(frame, (x, y - 30), (x + 80, y), color, -1)
                    cv2.putText(frame, label, (x + 5, y - 8),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                    
                    # Draw center point
                    cx, cy = obj['center']
                    cv2.circle(frame, (cx, cy), 5, color, -1)
                
                # Info text
                info = f"Tracking: ON | Active Tracks: {len(tracked_objects)}"
                cv2.putText(frame, info, (10, 30),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            else:
                # Just draw detections without tracking
                for det in detections:
                    x, y, w, h = det['bbox']
                    x, y, w, h = int(x), int(y), int(w), int(h)
                    
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                
                info = f"Tracking: OFF | Detections: {len(detections)}"
                cv2.putText(frame, info, (10, 30),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            
            # Show
            cv2.imshow("Smart Retail Analytics", frame)
            
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('s'):
                cv2.imwrite("detection_snapshot.jpg", frame)
                print("✅ Snapshot saved!")
            elif key == ord('t'):
                use_tracking = not use_tracking
                if use_tracking:
                    tracker.reset()
                print(f"✅ Tracking {'ON' if use_tracking else 'OFF'}")
    
    finally:
        video.release()
        cv2.destroyAllWindows()
        print(f"✅ Processed {frame_count} frames")


def run_video_analysis(video_path):
    """Process a video file."""
    print("\n" + "="*60)
    print("SMART RETAIL ANALYTICS - VIDEO ANALYSIS")
    print("="*60)
    print(f"Input: {video_path}")
    print("="*60 + "\n")
    
    video_path = Path(video_path)
    
    if not video_path.exists():
        print(f"❌ Video file not found: {video_path}")
        return
    
    # Initialize
    detector = PersonDetector()
    tracker = PersonTracker()  # NEW: Add tracker
    video = VideoHandler(source=video_path)
    
    # Output
    output_path = PROCESSED_VIDEOS_DIR / f"tracked_{video_path.name}"
    writer = VideoWriter(output_path, video.fps, video.frame_width, video.frame_height)
    
    # Colors for track IDs
    colors = [
        (255, 0, 0), (0, 255, 0), (0, 0, 255),
        (255, 255, 0), (255, 0, 255), (0, 255, 255),
        (128, 0, 0), (0, 128, 0), (0, 0, 128)
    ]
    
    frame_count = 0
    total_detections = 0
    
    try:
        print("🎬 Processing video with tracking...\n")
        
        while True:
            ret, frame = video.read_frame()
            if not ret:
                break
            
            frame_count += 1
            
            # Detect
            detections, _ = detector.detect(frame)
            total_detections += len(detections)
            
            # Track
            tracked_objects = tracker.update(detections)
            
            # Draw tracked objects
            for obj in tracked_objects:
                x, y, w, h = [int(v) for v in obj['bbox']]
                track_id = obj['id']
                color = colors[track_id % len(colors)]
                
                # Draw box
                cv2.rectangle(frame, (x, y), (x + w, y + h), color, 3)
                
                # Draw ID label
                label = f"ID:{track_id}"
                cv2.rectangle(frame, (x, y - 30), (x + 80, y), color, -1)
                cv2.putText(frame, label, (x + 5, y - 8),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            # Draw info
            info = f"Tracks: {len(tracked_objects)}"
            cv2.putText(frame, info, (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            # Save
            writer.write_frame(frame)
            
            # Progress
            if frame_count % 30 == 0:
                progress = video.get_progress()
                print(f"Progress: {progress:.1f}% | Frame {frame_count}/{video.total_frames}")
        
        print(f"\n✅ Analysis complete!")
        print(f"Frames processed: {frame_count}")
        print(f"Total detections: {total_detections}")
        print(f"Unique people tracked: {tracker.get_track_count()}")
        print(f"Output: {output_path}")
    
    finally:
        video.release()
        writer.release()


def run_occupancy_video(video_path, redefine_zone=False):
    """
    Run zone-based occupancy tracking on video file.
    
    This is the NEW Phase 4 approach using geometric zones instead of lines.
    More reliable and works with any camera angle!
    
    Args:
        video_path: Path to video file
        redefine_zone: Force zone reselection (ignore saved zone)
    """
    print("\n" + "="*60)
    print("PHASE 4: ZONE-BASED OCCUPANCY TRACKING - VIDEO ANALYSIS")
    print("="*60)
    print(f"Input: {video_path}")
    print("="*60 + "\n")
    
    video_path = Path(video_path)
    if not video_path.exists():
        print(f"❌ Video not found: {video_path}")
        return
    
    # Initialize
    detector = PersonDetector()
    tracker = PersonTracker(max_age=MAX_DISAPPEARED, min_hits=3, iou_threshold=0.3)
    video = VideoHandler(source=str(video_path))
    
    # Get first frame for zone selection
    ret, first_frame = video.read_frame()
    if not ret:
        print("❌ Failed to read video")
        return
    
    height, width = first_frame.shape[:2]
    video.reset()  # Reset to start
    
    # Calculate duration
    duration = video.total_frames / video.fps if video.fps > 0 else 0
    
    print(f"\n{'='*60}")
    print("VIDEO INFORMATION")
    print(f"{'='*60}")
    print(f"Source: {video_path}")
    print(f"FPS: {video.fps}")
    print(f"Resolution: {width} x {height}")
    print(f"Total Frames: {video.total_frames}")
    print(f"Duration: {duration:.2f} seconds")
    print(f"{'='*60}\n")
    
    # Load or create zone
    zone_points = None
    
    if not redefine_zone:
        zone_points = ZoneSelector.load_zone(str(video_path))
        if zone_points is not None:
            print("✅ Loaded saved zone from previous session")
            print("   (Use --redefine-zone flag to reselect zone)\n")
    else:
        print("🔄 Redefining zone (--redefine-zone flag used)\n")
    
    if zone_points is None:
        print("📍 Starting zone selection...")
        print("   Define the store boundary by clicking points on the frame.\n")
        
        selector = ZoneSelector(first_frame, "Define Store Zone")
        zone_points = selector.select_zone()
        
        if zone_points is None:
            print("❌ Zone selection cancelled")
            return
        
        # Save zone for future use
        ZoneSelector.save_zone(zone_points, str(video_path))
    else:
        print(f"✅ Using saved zone with {len(zone_points)} points")
    
    # Initialize occupancy tracker
    tracker_occ = OccupancyTracker(
        frame_height=height,
        frame_width=width,
        zone_points=zone_points,
        enable_logging=ENABLE_FOOTFALL_LOGGING
    )
    
    # Output video
    output_path = PROCESSED_VIDEOS_DIR / f"occupancy_{video_path.name}"
    writer = VideoWriter(output_path, video.fps, video.frame_width, video.frame_height)
    
    # Colors for track IDs
    colors = [
        (255, 0, 0), (0, 255, 0), (0, 0, 255),
        (255, 255, 0), (255, 0, 255), (0, 255, 255),
        (128, 0, 0), (0, 128, 0), (0, 0, 128)
    ]
    
    frame_count = 0
    
    try:
        print("🎬 Processing video with occupancy tracking...\n")
        
        while True:
            ret, frame = video.read_frame()
            if not ret:
                break
            
            frame_count += 1
            
            # Detect people
            detections, _ = detector.detect(frame)
            
            # Track people
            tracked_objects = tracker.update(detections)
            
            # Update occupancy tracker
            stats = tracker_occ.update(tracked_objects, frame_count)
            
            # Draw tracked objects
            for obj in tracked_objects:
                x, y, w, h = [int(v) for v in obj['bbox']]
                track_id = obj['id']
                color = colors[track_id % len(colors)]
                
                # Check if person is inside zone
                cx, cy = obj['center']
                is_inside = ZoneSelector.point_in_polygon((cx, cy), zone_points)
                
                # Draw box (green if inside, red if outside)
                box_color = (0, 255, 0) if is_inside else (0, 0, 255)
                cv2.rectangle(frame, (x, y), (x + w, y + h), box_color, 2)
                
                # Draw ID
                label = f"ID:{track_id}" + (" IN" if is_inside else " OUT")
                label_bg_color = (0, 200, 0) if is_inside else (0, 0, 200)
                label_width = 100 if is_inside else 110
                cv2.rectangle(frame, (x, y - 25), (x + label_width, y), label_bg_color, -1)
                cv2.putText(frame, label, (x + 5, y - 7),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                
                # Draw center
                cv2.circle(frame, (cx, cy), 4, box_color, -1)
            
            # Draw zone boundary
            frame = tracker_occ.draw_zone(frame)
            
            # Draw statistics
            frame = tracker_occ.draw_stats(frame, position='top-right')
            
            # Write frame
            writer.write_frame(frame)
            
            # Progress update
            if frame_count % 30 == 0:
                progress = (frame_count / video.total_frames) * 100
                print(f"Processed {frame_count} frames ({progress:.1f}%) | Occupancy: {stats['occupancy']} | Peak: {stats['max_occupancy']}")
        
        print(f"\n✅ Processing complete!")
        print(f"Processed {frame_count} frames")
        
        # Print summary
        tracker_occ.print_summary()
        
        print(f"📹 Output saved: {output_path}")
    
    finally:
        video.release()
        writer.release()


def run_occupancy_webcam():
    """
    Run zone-based occupancy tracking on webcam.
    
    Real-time occupancy counting using zone selection.
    """
    print("\n" + "="*60)
    print("PHASE 4: ZONE-BASED OCCUPANCY TRACKING - WEBCAM")
    print("="*60)
    print("Controls:")
    print("  'q' - Quit and show summary")
    print("  's' - Save snapshot")
    print("  'r' - Reset counters")
    print("="*60 + "\n")
    
    # Initialize
    detector = PersonDetector()
    tracker = PersonTracker(max_age=30, min_hits=3, iou_threshold=0.3)
    video = VideoHandler(use_webcam=True)
    
    # Get first frame for zone selection
    ret, first_frame = video.read_frame()
    if not ret:
        print("❌ Failed to read from webcam")
        return
    
    height, width = first_frame.shape[:2]
    
    print(f"Webcam resolution: {width}x{height}\n")
    print("📍 Define the store zone by clicking points on the frame.")
    print("   This zone represents the area to count occupancy.\n")
    
    # Zone selection
    selector = ZoneSelector(first_frame, "Define Store Zone - Webcam")
    zone_points = selector.select_zone()
    
    if zone_points is None:
        print("❌ Zone selection cancelled")
        return
    
    # Initialize occupancy tracker
    tracker_occ = OccupancyTracker(
        frame_height=height,
        frame_width=width,
        zone_points=zone_points,
        enable_logging=True
    )
    
    # Colors
    colors = [
        (255, 0, 0), (0, 255, 0), (0, 0, 255),
        (255, 255, 0), (255, 0, 255), (0, 255, 255),
        (128, 0, 128), (255, 165, 0), (0, 128, 128)
    ]
    
    frame_count = 0
    
    print("✅ System ready! Walk in/out of the zone to test.\n")
    
    # Create window with proper settings for maximize support
    window_name = 'Zone-Based Occupancy Tracking'
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)  # WINDOW_NORMAL allows resizing and maximize
    cv2.resizeWindow(window_name, 1280, 720)  # Set initial size
    
    try:
        while True:
            ret, frame = video.read_frame()
            if not ret:
                break
            
            frame_count += 1
            
            # Detect people
            detections, _ = detector.detect(frame)
            
            # Track people
            tracked_objects = tracker.update(detections)
            
            # Update occupancy
            stats = tracker_occ.update(tracked_objects, frame_count)
            
            # Draw tracked objects
            for obj in tracked_objects:
                x, y, w, h = [int(v) for v in obj['bbox']]
                track_id = obj['id']
                
                # Check if inside zone
                cx, cy = obj['center']
                is_inside = ZoneSelector.point_in_polygon((cx, cy), zone_points)
                
                # Color based on inside/outside
                box_color = (0, 255, 0) if is_inside else (0, 0, 255)
                cv2.rectangle(frame, (x, y), (x + w, y + h), box_color, 2)
                
                # Label
                label = f"ID:{track_id}" + (" IN" if is_inside else " OUT")
                label_bg = (0, 200, 0) if is_inside else (0, 0, 200)
                label_w = 100 if is_inside else 110
                cv2.rectangle(frame, (x, y - 25), (x + label_w, y), label_bg, -1)
                cv2.putText(frame, label, (x + 5, y - 7),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                
                # Center point
                cv2.circle(frame, (cx, cy), 4, box_color, -1)
            
            # Draw zone
            frame = tracker_occ.draw_zone(frame)
            
            # Draw stats
            frame = tracker_occ.draw_stats(frame, position='top-right')
            
            # Display
            cv2.imshow('Zone-Based Occupancy Tracking', frame)
            
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('s'):
                snapshot_path = OUTPUTS_DIR / f"occupancy_snapshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
                cv2.imwrite(str(snapshot_path), frame)
                print(f"📸 Snapshot saved: {snapshot_path}")
        
        # Summary
        tracker_occ.print_summary()
    
    finally:
        video.release()
        cv2.destroyAllWindows()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Smart Retail Analytics System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --webcam                    # Live webcam detection
  python main.py --video store_footage.mp4   # Process video file
  python main.py --demo                      # Quick demo mode
        """
    )
    
    parser.add_argument('--webcam', action='store_true',
                        help='Use webcam for real-time detection')
    parser.add_argument('--video', type=str,
                        help='Path to video file to process')
    parser.add_argument('--footfall', action='store_true',
                        help='Enable footfall counting - LINE-BASED (Phase 4 - OLD)')
    parser.add_argument('--occupancy', action='store_true',
                        help='Enable occupancy tracking - ZONE-BASED (Phase 4 - NEW, RECOMMENDED)')
    parser.add_argument('--redefine-zone', action='store_true',
                        help='Force zone reselection (ignore saved zone)')
    parser.add_argument('--demo', action='store_true',
                        help='Run demo mode (webcam)')
    
    args = parser.parse_args()
    
    # Show header
    print("\n" + "="*60)
    print(" "*15 + "SMART RETAIL ANALYTICS")
    print(" "*10 + "Computer Vision for Retail Insights")
    print("="*60)
    
    if args.webcam or args.demo:
        if args.occupancy:
            run_occupancy_webcam()
        elif args.footfall:
            run_footfall_demo()
        else:
            run_webcam_demo()
    elif args.video:
        if args.occupancy:
            run_occupancy_video(args.video, redefine_zone=args.redefine_zone)
        elif args.footfall:
            run_footfall_video(args.video)
        else:
            run_video_analysis(args.video)
    else:
        print("\n❌ No mode specified!")
        print("\nUsage:")
        print("  python main.py --webcam                             # Live detection")
        print("  python main.py --webcam --occupancy                 # Live occupancy (ZONE-BASED, RECOMMENDED)")
        print("  python main.py --webcam --footfall                  # Live footfall (LINE-BASED, OLD)")
        print("  python main.py --video video.mp4                    # Process video")
        print("  python main.py --video video.mp4 --occupancy        # Video with occupancy (RECOMMENDED)")
        print("  python main.py --video video.mp4 --occupancy --redefine-zone  # Reselect zone")
        print("  python main.py --video video.mp4 --footfall         # Video with footfall (OLD)")
        print("\nFor help: python main.py --help")


if __name__ == "__main__":
    main()
