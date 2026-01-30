"""
Person Detection Module using YOLOv8

This module handles person detection in video frames using the YOLOv8 model.

LEARNING POINTS:
- YOLO object detection
- Bounding box coordinates
- Confidence thresholding
- Class filtering
- Model inference

Author: Smart Retail Analytics Team
"""

import cv2
import numpy as np
from pathlib import Path
import sys

# Import ultralytics YOLO
try:
    from ultralytics import YOLO
except ImportError:
    print("❌ Ultralytics not installed. Run: pip install ultralytics")
    sys.exit(1)

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))
from config import *


class PersonDetector:
    """
    A class to detect persons in video frames using YOLOv8.
    
    The detector:
    1. Loads a pre-trained YOLO model
    2. Processes frames to find people
    3. Filters detections by confidence
    4. Returns bounding boxes for detected persons
    
    Attributes:
        model: YOLOv8 model instance
        confidence_threshold: Minimum confidence for detection (0.0-1.0)
        person_class_id: COCO dataset class ID for 'person' (0)
    """
    
    def __init__(self, model_name=None, confidence_threshold=None):
        """
        Initialize the Person Detector.
        
        Args:
            model_name: YOLO model to use (default from config)
            confidence_threshold: Min confidence (default from config)
        
        LEARNING: __init__ is called when you create an object:
        detector = PersonDetector()  ← This calls __init__
        """
        # Use config values if not provided
        self.model_name = model_name or YOLO_MODEL
        self.confidence_threshold = confidence_threshold or CONFIDENCE_THRESHOLD
        self.person_class_id = PERSON_CLASS_ID
        
        # Model will be loaded on first use (lazy loading)
        self.model = None
        self.device = 'cuda' if USE_GPU else 'cpu'
        
        print(f"\n{'='*60}")
        print("PERSON DETECTOR INITIALIZED")
        print(f"{'='*60}")
        print(f"Model: {self.model_name}")
        print(f"Confidence Threshold: {self.confidence_threshold}")
        print(f"Device: {self.device.upper()}")
        print(f"{'='*60}\n")
        
        # Load model
        self._load_model()
    
    def _load_model(self):
        """
        Load the YOLO model.
        
        LEARNING: The first time you run this, YOLO will:
        1. Download the model weights (~6MB for yolov8n)
        2. Cache them in your home directory
        3. Load them into memory
        
        Subsequent runs will use the cached model (fast!)
        """
        try:
            print(f"📥 Loading YOLO model: {self.model_name}...")
            
            # Check if model exists in our models directory
            model_path = get_model_path(self.model_name)
            
            if model_path.exists():
                print(f"✅ Found model at: {model_path}")
                self.model = YOLO(str(model_path))
            else:
                print(f"⏬ Model not found locally. Downloading {self.model_name}...")
                print("   (This happens only once, ~6MB download)")
                self.model = YOLO(self.model_name)
                print(f"✅ Model downloaded and loaded!")
            
            # Move model to appropriate device (GPU/CPU)
            if USE_GPU:
                try:
                    self.model.to('cuda')
                    print("✅ Model moved to GPU (CUDA)")
                except Exception as e:
                    print(f"⚠️  GPU not available, using CPU: {e}")
                    self.model.to('cpu')
                    self.device = 'cpu'
            else:
                self.model.to('cpu')
                print("✅ Model running on CPU")
            
            print(f"✅ Model ready for inference!\n")
            
        except Exception as e:
            print(f"❌ Error loading model: {e}")
            print("\nTroubleshooting:")
            print("1. Check internet connection (for first download)")
            print("2. Try: pip install --upgrade ultralytics")
            print("3. Try a different model: yolov8n.pt")
            sys.exit(1)
    
    def detect(self, frame, return_annotated=False):
        """
        Detect persons in a frame.
        
        Args:
            frame: Input frame (numpy array, BGR format)
            return_annotated: If True, return frame with boxes drawn
        
        Returns:
            detections: List of detection dictionaries
            annotated_frame: (Optional) Frame with boxes drawn
        
        LEARNING: This is the core detection function!
        It takes a frame and returns where people are.
        
        Detection format:
        {
            'bbox': (x, y, width, height),      # Bounding box
            'confidence': 0.87,                  # How confident (0-1)
            'class': 0,                         # Class ID (0 = person)
            'class_name': 'person',             # Human-readable name
            'center': (x_center, y_center)      # Box center point
        }
        """
        if self.model is None:
            print("❌ Model not loaded!")
            return [], frame
        
        if frame is None:
            print("❌ Invalid frame!")
            return [], None
        
        # Run YOLO inference
        # verbose=False suppresses the output messages
        results = self.model(frame, conf=self.confidence_threshold, verbose=False)
        
        # Extract detections
        detections = self._parse_results(results[0])
        
        # Optionally draw boxes on frame
        if return_annotated:
            annotated_frame = self._draw_detections(frame.copy(), detections)
            return detections, annotated_frame
        
        return detections, frame
    
    def _parse_results(self, result):
        """
        Parse YOLO results into a clean format.
        
        Args:
            result: YOLO result object
        
        Returns:
            List of detection dictionaries
        
        LEARNING: YOLO returns a complex object.
        This function extracts only what we need.
        """
        detections = []
        
        # Get boxes, confidences, and classes
        boxes = result.boxes
        
        if boxes is None or len(boxes) == 0:
            return detections  # No detections
        
        # Iterate through each detection
        for box in boxes:
            # Get class ID
            class_id = int(box.cls[0])
            
            # Filter: Only keep 'person' class
            if class_id != self.person_class_id:
                continue
            
            # Get confidence
            confidence = float(box.conf[0])
            
            # Get bounding box coordinates
            # xyxy format: [x1, y1, x2, y2]
            x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
            
            # Convert to (x, y, width, height) format
            x = int(x1)
            y = int(y1)
            width = int(x2 - x1)
            height = int(y2 - y1)
            
            # Calculate center point
            center_x = int(x + width / 2)
            center_y = int(y + height / 2)
            
            # Create detection dictionary
            detection = {
                'bbox': (x, y, width, height),
                'confidence': confidence,
                'class': class_id,
                'class_name': 'person',
                'center': (center_x, center_y)
            }
            
            detections.append(detection)
        
        return detections
    
    def _draw_detections(self, frame, detections):
        """
        Draw bounding boxes and labels on frame.
        
        Args:
            frame: Input frame
            detections: List of detection dictionaries
        
        Returns:
            Frame with drawn detections
        
        LEARNING: This visualizes what the detector found.
        Essential for debugging and demos!
        """
        for detection in detections:
            # Extract info
            x, y, w, h = detection['bbox']
            confidence = detection['confidence']
            center_x, center_y = detection['center']
            
            # Choose color based on confidence
            # High confidence = Green, Low = Yellow/Red
            if confidence > 0.8:
                color = (0, 255, 0)  # Green
            elif confidence > 0.6:
                color = (0, 255, 255)  # Yellow
            else:
                color = (0, 165, 255)  # Orange
            
            # Draw bounding box
            cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
            
            # Draw center point
            cv2.circle(frame, (center_x, center_y), 4, color, -1)
            
            # Prepare label text
            label = f"Person {confidence:.2f}"
            
            # Calculate label size for background
            (label_width, label_height), baseline = cv2.getTextSize(
                label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1
            )
            
            # Draw label background (black rectangle)
            cv2.rectangle(
                frame,
                (x, y - label_height - baseline - 5),
                (x + label_width, y),
                color,
                -1  # Filled rectangle
            )
            
            # Draw label text (white text)
            cv2.putText(
                frame,
                label,
                (x, y - baseline - 5),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 0, 0),  # Black text
                1,
                cv2.LINE_AA
            )
        
        # Draw detection count
        count_text = f"Detected: {len(detections)} person(s)"
        cv2.putText(
            frame,
            count_text,
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 0),
            2,
            cv2.LINE_AA
        )
        
        return frame
    
    def detect_batch(self, frames):
        """
        Detect persons in multiple frames (batch processing).
        
        Args:
            frames: List of frames
        
        Returns:
            List of detection lists (one per frame)
        
        LEARNING: Batch processing is more efficient than
        processing frames one-by-one when you have many frames.
        """
        if self.model is None:
            print("❌ Model not loaded!")
            return []
        
        all_detections = []
        
        # Process all frames
        results = self.model(frames, conf=self.confidence_threshold, verbose=False)
        
        # Parse each result
        for result in results:
            detections = self._parse_results(result)
            all_detections.append(detections)
        
        return all_detections
    
    def get_detection_count(self, frame):
        """
        Quick function to just get count of people.
        
        Args:
            frame: Input frame
        
        Returns:
            int: Number of people detected
        """
        detections, _ = self.detect(frame)
        return len(detections)


# ==================== DEMO/TESTING CODE ====================

def test_detector_on_webcam():
    """
    Test the person detector with webcam.
    
    This demo:
    1. Opens webcam
    2. Detects people in each frame
    3. Draws bounding boxes
    4. Shows FPS and count
    """
    print("\n" + "="*60)
    print("TESTING PERSON DETECTOR WITH WEBCAM")
    print("="*60)
    print("Press 'q' to quit")
    print("Press 's' to save current frame")
    print("="*60 + "\n")
    
    # Import video handler
    sys.path.append(str(Path(__file__).parent.parent))
    from utils.video_handler import VideoHandler
    
    # Initialize components
    detector = PersonDetector()
    video = VideoHandler(use_webcam=True)
    
    frame_count = 0
    fps_start_time = cv2.getTickCount()
    fps = 0
    
    try:
        while True:
            # Read frame
            ret, frame = video.read_frame()
            if not ret:
                break
            
            frame_count += 1
            
            # Detect persons
            detections, annotated_frame = detector.detect(frame, return_annotated=True)
            
            # Calculate FPS
            if frame_count % 30 == 0:  # Update FPS every 30 frames
                fps_end_time = cv2.getTickCount()
                time_diff = (fps_end_time - fps_start_time) / cv2.getTickFrequency()
                fps = 30 / time_diff
                fps_start_time = fps_end_time
            
            # Draw FPS on frame
            fps_text = f"FPS: {fps:.1f}"
            cv2.putText(
                annotated_frame,
                fps_text,
                (10, 60),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255, 255, 0),
                2,
                cv2.LINE_AA
            )
            
            # Print detection info (every 30 frames to avoid spam)
            if frame_count % 30 == 0:
                print(f"Frame {frame_count}: Detected {len(detections)} person(s) | FPS: {fps:.1f}")
            
            # Display frame
            cv2.imshow("Person Detection - Press 'q' to quit", annotated_frame)
            
            # Handle keyboard input
            key = cv2.waitKey(1) & 0xFF
            
            if key == ord('q'):
                print("\n✅ User pressed 'q'. Exiting...")
                break
            elif key == ord('s'):
                # Save current frame
                output_path = OUTPUTS_DIR / "test_detection.jpg"
                cv2.imwrite(str(output_path), annotated_frame)
                print(f"✅ Frame saved to: {output_path}")
    
    except KeyboardInterrupt:
        print("\n✅ Interrupted by user")
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Clean up
        video.release()
        cv2.destroyAllWindows()
        print(f"\n✅ Test completed. Processed {frame_count} frames.")
        print(f"Average FPS: {fps:.1f}")


def test_detector_on_video(video_path):
    """
    Test the person detector on a video file.
    
    Args:
        video_path: Path to video file
    """
    print("\n" + "="*60)
    print(f"TESTING PERSON DETECTOR ON VIDEO")
    print("="*60)
    print(f"Video: {video_path}")
    print("="*60 + "\n")
    
    # Import required modules
    sys.path.append(str(Path(__file__).parent.parent))
    from utils.video_handler import VideoHandler, VideoWriter
    
    # Initialize detector
    detector = PersonDetector()
    
    # Open video
    video = VideoHandler(source=video_path)
    
    # Prepare output video
    output_path = PROCESSED_VIDEOS_DIR / f"detected_{Path(video_path).name}"
    writer = VideoWriter(
        output_path,
        video.fps,
        video.frame_width,
        video.frame_height
    )
    
    frame_count = 0
    total_detections = 0
    
    try:
        print("Processing video...")
        
        while True:
            ret, frame = video.read_frame()
            if not ret:
                break
            
            frame_count += 1
            
            # Detect persons
            detections, annotated_frame = detector.detect(frame, return_annotated=True)
            total_detections += len(detections)
            
            # Write to output video
            writer.write_frame(annotated_frame)
            
            # Show progress
            if frame_count % 30 == 0:
                progress = video.get_progress()
                print(f"Progress: {progress:.1f}% | Frame {frame_count}/{video.total_frames}")
            
            # Display (optional)
            if DISPLAY_FRAME:
                cv2.imshow("Processing...", annotated_frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    print("Processing stopped by user")
                    break
        
        print(f"\n✅ Processing complete!")
        print(f"Total frames: {frame_count}")
        print(f"Total detections: {total_detections}")
        print(f"Average detections per frame: {total_detections/frame_count:.2f}")
        print(f"Output saved to: {output_path}")
    
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        video.release()
        writer.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    """
    Run this file directly to test the detector.
    
    Usage:
        python person_detector.py               # Test with webcam
        python person_detector.py video.mp4     # Test with video file
    """
    import sys
    
    if len(sys.argv) > 1:
        # Video file provided
        video_path = sys.argv[1]
        test_detector_on_video(video_path)
    else:
        # No arguments, use webcam
        test_detector_on_webcam()
