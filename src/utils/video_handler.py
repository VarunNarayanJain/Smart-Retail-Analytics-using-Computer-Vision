"""
Video Handler Module

This module handles all video input/output operations:
- Reading video files
- Capturing webcam feed
- Writing processed videos
- Frame extraction and manipulation

LEARNING POINTS:
- OpenCV VideoCapture and VideoWriter
- Frame manipulation
- FPS calculation
- Error handling for video operations
"""

import cv2
import numpy as np
from pathlib import Path
import sys

# Add parent directory to path to import config
sys.path.append(str(Path(__file__).parent.parent))
from config import *


class VideoHandler:
    """
    A class to handle video input/output operations.
    
    Attributes:
        source: Video file path or webcam index
        cap: OpenCV VideoCapture object
        fps: Frames per second of the video
        frame_width: Width of video frames
        frame_height: Height of video frames
        total_frames: Total number of frames in video
    """
    
    def __init__(self, source=None, use_webcam=False):
        """
        Initialize the VideoHandler.
        
        Args:
            source: Path to video file or webcam index
            use_webcam: Boolean to use webcam instead of file
        """
        self.source = source
        self.use_webcam = use_webcam
        self.cap = None
        self.fps = 0
        self.frame_width = 0
        self.frame_height = 0
        self.total_frames = 0
        self.current_frame = 0
        
        self._initialize_capture()
    
    def _initialize_capture(self):
        """
        Initialize the video capture object.
        
        LEARNING: VideoCapture can take:
        - Integer (webcam index): cv2.VideoCapture(0)
        - String (file path): cv2.VideoCapture('video.mp4')
        """
        try:
            if self.use_webcam:
                print(f"📹 Opening webcam (index: {WEBCAM_INDEX})...")
                self.cap = cv2.VideoCapture(WEBCAM_INDEX)
            else:
                if self.source is None:
                    print("❌ Error: No video source provided!")
                    return False
                
                print(f"📹 Opening video file: {self.source}")
                self.cap = cv2.VideoCapture(str(self.source))
            
            # Check if video opened successfully
            if not self.cap.isOpened():
                print("❌ Error: Could not open video source!")
                return False
            
            # Get video properties
            self.fps = int(self.cap.get(cv2.CAP_PROP_FPS))
            self.frame_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            self.frame_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
            print(f"✅ Video source opened successfully!")
            self._print_video_info()
            return True
            
        except Exception as e:
            print(f"❌ Error initializing video capture: {e}")
            return False
    
    def _print_video_info(self):
        """Print video information."""
        print("\n" + "="*50)
        print("VIDEO INFORMATION")
        print("="*50)
        print(f"Source: {'Webcam' if self.use_webcam else self.source}")
        print(f"FPS: {self.fps}")
        print(f"Resolution: {self.frame_width} x {self.frame_height}")
        if not self.use_webcam:
            print(f"Total Frames: {self.total_frames}")
            duration = self.total_frames / self.fps if self.fps > 0 else 0
            print(f"Duration: {duration:.2f} seconds")
        print("="*50 + "\n")
    
    def read_frame(self):
        """
        Read the next frame from the video.
        
        Returns:
            tuple: (success, frame) where success is a boolean and frame is numpy array
        
        LEARNING: cap.read() returns two values:
        - ret: Boolean indicating if frame was read successfully
        - frame: The actual frame as a numpy array (BGR format)
        """
        if self.cap is None or not self.cap.isOpened():
            return False, None
        
        ret, frame = self.cap.read()
        
        if ret:
            self.current_frame += 1
        
        return ret, frame
    
    def release(self):
        """
        Release the video capture object.
        
        LEARNING: Always release resources when done!
        This frees up memory and closes file handles.
        """
        if self.cap is not None:
            self.cap.release()
            print("✅ Video capture released.")
    
    def get_progress(self):
        """
        Get current progress percentage.
        
        Returns:
            float: Progress percentage (0-100)
        """
        if self.total_frames == 0:
            return 0
        return (self.current_frame / self.total_frames) * 100
    
    @staticmethod
    def display_frame(frame, window_name="Frame", wait_time=1):
        """
        Display a frame in a window.
        
        Args:
            frame: Frame to display
            window_name: Name of the display window
            wait_time: Time to wait in milliseconds (0 = wait forever)
        
        Returns:
            int: Key pressed by user (-1 if no key pressed)
        
        LEARNING: 
        - cv2.imshow() displays the frame
        - cv2.waitKey() waits for keyboard input
        - waitKey(1) waits 1ms, waitKey(0) waits forever
        - Press 'q' to quit is a common convention
        """
        if frame is None:
            return -1
        
        cv2.imshow(window_name, frame)
        key = cv2.waitKey(wait_time) & 0xFF
        return key
    
    @staticmethod
    def resize_frame(frame, width=None, height=None):
        """
        Resize a frame to specified dimensions.
        
        Args:
            frame: Input frame
            width: Target width (None to maintain aspect ratio)
            height: Target height (None to maintain aspect ratio)
        
        Returns:
            Resized frame
        
        LEARNING: Resizing reduces processing time but may lose detail.
        """
        if frame is None:
            return None
        
        if width is None and height is None:
            return frame
        
        h, w = frame.shape[:2]
        
        if width is None:
            # Calculate width maintaining aspect ratio
            aspect_ratio = height / h
            width = int(w * aspect_ratio)
        elif height is None:
            # Calculate height maintaining aspect ratio
            aspect_ratio = width / w
            height = int(h * aspect_ratio)
        
        resized = cv2.resize(frame, (width, height), interpolation=cv2.INTER_AREA)
        return resized
    
    @staticmethod
    def draw_text(frame, text, position, color=(0, 255, 0), scale=0.6, thickness=2):
        """
        Draw text on a frame.
        
        Args:
            frame: Frame to draw on
            text: Text to display
            position: (x, y) position
            color: BGR color tuple
            scale: Font scale
            thickness: Line thickness
        
        LEARNING: Text is useful for displaying info on frames.
        """
        cv2.putText(frame, text, position, cv2.FONT_HERSHEY_SIMPLEX, 
                    scale, color, thickness, cv2.LINE_AA)
        return frame


class VideoWriter:
    """
    A class to write processed video frames to a file.
    
    LEARNING: VideoWriter saves frames as a video file.
    """
    
    def __init__(self, output_path, fps, frame_width, frame_height):
        """
        Initialize video writer.
        
        Args:
            output_path: Path to save video
            fps: Frames per second
            frame_width: Width of frames
            frame_height: Height of frames
        """
        self.output_path = Path(output_path)
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Define codec and create VideoWriter
        # 'mp4v' for .mp4, 'XVID' for .avi
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        
        self.writer = cv2.VideoWriter(
            str(self.output_path),
            fourcc,
            fps,
            (frame_width, frame_height)
        )
        
        if not self.writer.isOpened():
            print(f"❌ Error: Could not open video writer for {output_path}")
        else:
            print(f"✅ Video writer initialized: {output_path}")
    
    def write_frame(self, frame):
        """Write a frame to the video file."""
        if self.writer is not None and self.writer.isOpened():
            self.writer.write(frame)
    
    def release(self):
        """Release the video writer."""
        if self.writer is not None:
            self.writer.release()
            print(f"✅ Video saved: {self.output_path}")


# ==================== TESTING CODE ====================
def test_video_handler():
    """
    Test function to demonstrate VideoHandler usage.
    
    This will:
    1. Try to open webcam
    2. Read and display frames
    3. Show how to process frames
    """
    print("\n🧪 Testing VideoHandler with Webcam...")
    print("Press 'q' to quit\n")
    
    # Initialize video handler with webcam
    vh = VideoHandler(use_webcam=True)
    
    frame_count = 0
    
    try:
        while True:
            # Read frame
            ret, frame = vh.read_frame()
            
            if not ret:
                print("❌ Failed to read frame")
                break
            
            frame_count += 1
            
            # Draw some info on the frame
            info_text = f"Frame: {frame_count} | FPS: {vh.fps} | Press 'q' to quit"
            frame = vh.draw_text(frame, info_text, (10, 30), 
                                color=(0, 255, 255), scale=0.7, thickness=2)
            
            # Display the frame
            key = vh.display_frame(frame, "Webcam Test")
            
            # Press 'q' to quit
            if key == ord('q'):
                print("\n✅ User pressed 'q'. Exiting...")
                break
    
    except KeyboardInterrupt:
        print("\n✅ Interrupted by user")
    
    finally:
        # Always release resources
        vh.release()
        cv2.destroyAllWindows()
        print(f"\n✅ Test completed. Processed {frame_count} frames.")


if __name__ == "__main__":
    """
    When you run this file directly, it will test the video handler.
    
    To run: python video_handler.py
    """
    test_video_handler()
