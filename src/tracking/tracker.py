"""
Person Tracking Module using SORT Algorithm

This module implements the SORT (Simple Online and Realtime Tracking) algorithm
to track people across video frames.

SORT combines:
1. Kalman Filter - Predicts future position
2. Hungarian Algorithm - Optimal assignment
3. IOU - Measures bounding box overlap

LEARNING POINTS:
- Object tracking vs detection
- Kalman filter for motion prediction
- Data association problem
- Track lifecycle management

Author: Smart Retail Analytics Team
Reference: SORT paper by Alex Bewley et al.
"""

import numpy as np
from scipy.optimize import linear_sum_assignment
from filterpy.kalman import KalmanFilter
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))
from config import *


class KalmanBoxTracker:
    """
    Tracks a single person's bounding box using a Kalman Filter.
    
    The state is represented as [x, y, s, r, vx, vy, vs] where:
    - x, y: Center position of bounding box
    - s: Scale (area) of bounding box
    - r: Aspect ratio (width/height)
    - vx, vy, vs: Velocities
    
    LEARNING: Kalman Filter is like a smart guesser!
    It predicts where the person will be based on:
    1. Where they were before
    2. How fast they were moving
    3. Uncertainty in measurements
    """
    
    count = 0  # Class variable to generate unique IDs
    
    def __init__(self, bbox):
        """
        Initialize tracker for a detected person.
        
        Args:
            bbox: Bounding box (x, y, width, height)
        
        LEARNING: Each detection gets its own Kalman Filter
        to track its movement independently.
        """
        # Initialize Kalman Filter
        # 7 state variables, 4 measurement variables
        self.kf = KalmanFilter(dim_x=7, dim_z=4)
        
        # State transition matrix (how state evolves over time)
        # LEARNING: This says "position changes based on velocity"
        self.kf.F = np.array([
            [1, 0, 0, 0, 1, 0, 0],  # x' = x + vx
            [0, 1, 0, 0, 0, 1, 0],  # y' = y + vy
            [0, 0, 1, 0, 0, 0, 1],  # s' = s + vs
            [0, 0, 0, 1, 0, 0, 0],  # r' = r (aspect ratio constant)
            [0, 0, 0, 0, 1, 0, 0],  # vx' = vx
            [0, 0, 0, 0, 0, 1, 0],  # vy' = vy
            [0, 0, 0, 0, 0, 0, 1]   # vs' = vs
        ])
        
        # Measurement function (we measure position and size)
        # LEARNING: We can only measure x, y, s, r directly
        # Velocities are inferred by the filter
        self.kf.H = np.array([
            [1, 0, 0, 0, 0, 0, 0],
            [0, 1, 0, 0, 0, 0, 0],
            [0, 0, 1, 0, 0, 0, 0],
            [0, 0, 0, 1, 0, 0, 0]
        ])
        
        # Measurement noise (how much we trust measurements)
        # LEARNING: VERY LOW - Trust measurements MUCH MORE for real-time tracking
        # Lower values = minimal smoothing = fastest tracking response
        self.kf.R[2:, 2:] *= 0.5  # REDUCED from 1.0 to 0.5 for even faster response
        
        # Process noise (how much we trust the model)
        # LEARNING: INCREASED - Allow MORE velocity changes for responsive tracking
        # Higher = person can change velocity more freely
        self.kf.P[4:, 4:] *= 1000.  # High uncertainty in velocity
        self.kf.P *= 10.
        
        # Process noise covariance (motion model uncertainty)
        # INCREASED to allow faster adaptation to sudden movements
        self.kf.Q[-1, -1] *= 0.2  # DOUBLED from 0.1 to 0.2 for real-time responsiveness
        self.kf.Q[4:, 4:] *= 0.2  # DOUBLED from 0.1 to 0.2 for real-time responsiveness
        
        # Convert bbox to Kalman state
        self.kf.x[:4] = self._bbox_to_z(bbox)
        
        # Track properties
        self.time_since_update = 0
        self.id = KalmanBoxTracker.count
        KalmanBoxTracker.count += 1
        self.history = []
        self.hits = 0
        self.hit_streak = 0
        self.age = 0
        
    def update(self, bbox):
        """
        Update tracker with new detection.
        
        Args:
            bbox: New bounding box (x, y, width, height)
        
        LEARNING: This is called when we successfully match
        a detection to this track. Updates position!
        """
        self.time_since_update = 0
        self.history = []
        self.hits += 1
        self.hit_streak += 1
        
        # Update Kalman filter with new measurement
        self.kf.update(self._bbox_to_z(bbox))
        
    def predict(self):
        """
        Predict next position using Kalman filter.
        
        Returns:
            Predicted bounding box
        
        LEARNING: Called every frame to predict where
        the person should be, even if not detected!
        """
        # Predict next state
        if (self.kf.x[6] + self.kf.x[2]) <= 0:
            self.kf.x[6] *= 0.0
        
        self.kf.predict()
        self.age += 1
        
        if self.time_since_update > 0:
            self.hit_streak = 0
        
        self.time_since_update += 1
        self.history.append(self._z_to_bbox(self.kf.x))
        
        return self.history[-1]
    
    def get_state(self):
        """
        Get current bounding box position.
        
        Returns:
            Current bbox (x, y, width, height)
        """
        return self._z_to_bbox(self.kf.x)
    
    @staticmethod
    def _bbox_to_z(bbox):
        """
        Convert bounding box to Kalman filter measurement format.
        
        LEARNING: Converts (x, y, w, h) to (cx, cy, s, r)
        where cx, cy = center, s = area, r = aspect ratio
        """
        x, y, w, h = bbox
        cx = x + w / 2.0
        cy = y + h / 2.0
        s = w * h  # Area
        r = w / float(h)  # Aspect ratio
        return np.array([cx, cy, s, r]).reshape((4, 1))
    
    @staticmethod
    def _z_to_bbox(z):
        """
        Convert Kalman state back to bounding box.
        
        LEARNING: Converts (cx, cy, s, r) back to (x, y, w, h)
        """
        cx, cy, s, r = z[0], z[1], z[2], z[3]
        w = np.sqrt(s * r)
        h = s / w
        x = cx - w / 2.0
        y = cy - h / 2.0
        return np.array([x, y, w, h]).flatten()


def iou_batch(bboxes1, bboxes2):
    """
    Calculate IOU (Intersection over Union) between two sets of boxes.
    
    Args:
        bboxes1: Array of bboxes (x, y, w, h)
        bboxes2: Array of bboxes (x, y, w, h)
    
    Returns:
        IOU matrix (shape: len(bboxes1) x len(bboxes2))
    
    LEARNING: IOU measures how much two boxes overlap.
    1.0 = perfect overlap, 0.0 = no overlap
    """
    bboxes2 = np.expand_dims(bboxes2, 0)
    bboxes1 = np.expand_dims(bboxes1, 1)
    
    # Calculate coordinates of intersection
    xx1 = np.maximum(bboxes1[..., 0], bboxes2[..., 0])
    yy1 = np.maximum(bboxes1[..., 1], bboxes2[..., 1])
    xx2 = np.minimum(bboxes1[..., 0] + bboxes1[..., 2], 
                     bboxes2[..., 0] + bboxes2[..., 2])
    yy2 = np.minimum(bboxes1[..., 1] + bboxes1[..., 3], 
                     bboxes2[..., 1] + bboxes2[..., 3])
    
    # Calculate intersection area
    w = np.maximum(0., xx2 - xx1)
    h = np.maximum(0., yy2 - yy1)
    intersection = w * h
    
    # Calculate union area
    area1 = bboxes1[..., 2] * bboxes1[..., 3]
    area2 = bboxes2[..., 2] * bboxes2[..., 3]
    union = area1 + area2 - intersection
    
    # Calculate IOU
    iou = intersection / union
    
    return iou


def associate_detections_to_trackers(detections, trackers, iou_threshold=0.3):
    """
    Match detections to existing tracks using IOU and Hungarian algorithm.
    
    Args:
        detections: List of detected bboxes
        trackers: List of predicted tracker bboxes
        iou_threshold: Minimum IOU for valid match
    
    Returns:
        matches: Array of (detection_idx, tracker_idx) pairs
        unmatched_detections: Indices of unmatched detections
        unmatched_trackers: Indices of unmatched trackers
    
    LEARNING: This is the "data association" problem!
    Which detection corresponds to which track?
    """
    if len(trackers) == 0:
        return np.empty((0, 2), dtype=int), np.arange(len(detections)), np.empty((0,), dtype=int)
    
    # Calculate IOU matrix
    iou_matrix = iou_batch(detections, trackers)
    
    # Use Hungarian algorithm for optimal assignment
    # LEARNING: This finds the best overall matching, not just greedy!
    if min(iou_matrix.shape) > 0:
        # Convert IOU to cost (1 - IOU, since we want to minimize)
        cost_matrix = 1 - iou_matrix
        
        # Hungarian algorithm finds minimum cost assignment
        row_indices, col_indices = linear_sum_assignment(cost_matrix)
        
        # Filter out matches below threshold
        matches = []
        for row, col in zip(row_indices, col_indices):
            if iou_matrix[row, col] >= iou_threshold:
                matches.append([row, col])
        matches = np.array(matches)
    else:
        matches = np.empty((0, 2), dtype=int)
    
    # Find unmatched detections
    unmatched_detections = []
    for d in range(len(detections)):
        if len(matches) == 0 or d not in matches[:, 0]:
            unmatched_detections.append(d)
    
    # Find unmatched trackers
    unmatched_trackers = []
    for t in range(len(trackers)):
        if len(matches) == 0 or t not in matches[:, 1]:
            unmatched_trackers.append(t)
    
    return matches, np.array(unmatched_detections), np.array(unmatched_trackers)


class PersonTracker:
    """
    Multi-person tracker using SORT algorithm.
    
    Manages multiple KalmanBoxTracker instances to track all people.
    
    LEARNING: This is the main tracking class you'll use!
    It coordinates all individual trackers.
    """
    
    def __init__(self, max_age=30, min_hits=3, iou_threshold=0.3):
        """
        Initialize the tracker.
        
        Args:
            max_age: Maximum frames to keep track without detection
            min_hits: Minimum hits before track is confirmed
            iou_threshold: Minimum IOU for matching
        
        LEARNING: 
        - max_age: How long to remember a person after they disappear
        - min_hits: Ignore brief false detections
        - iou_threshold: How strict matching should be
        """
        self.max_age = max_age
        self.min_hits = min_hits
        self.iou_threshold = iou_threshold
        self.trackers = []
        self.frame_count = 0
        
        print(f"\n{'='*60}")
        print("PERSON TRACKER INITIALIZED")
        print(f"{'='*60}")
        print(f"Algorithm: SORT (Simple Online Realtime Tracking)")
        print(f"Max Age: {max_age} frames")
        print(f"Min Hits: {min_hits} frames")
        print(f"IOU Threshold: {iou_threshold}")
        print(f"{'='*60}\n")
    
    def update(self, detections):
        """
        Update tracker with new detections for current frame.
        
        Args:
            detections: List of detection dicts from PersonDetector
        
        Returns:
            List of tracked objects with IDs
        
        LEARNING: This is called once per frame!
        It's where all the magic happens.
        """
        self.frame_count += 1
        
        # Convert detections to numpy array format
        det_bboxes = np.array([d['bbox'] for d in detections]) if len(detections) > 0 else np.empty((0, 4))
        
        # Get predicted locations from existing trackers
        trk_bboxes = np.zeros((len(self.trackers), 4))
        to_del = []
        
        for t, trk in enumerate(self.trackers):
            pos = trk.predict()
            trk_bboxes[t] = pos
            
            # Mark invalid predictions for deletion
            if np.any(np.isnan(pos)):
                to_del.append(t)
        
        # Remove invalid trackers
        for t in reversed(to_del):
            self.trackers.pop(t)
        trk_bboxes = np.ma.compress_rows(np.ma.masked_invalid(trk_bboxes))
        
        # Associate detections to trackers
        matched, unmatched_dets, unmatched_trks = associate_detections_to_trackers(
            det_bboxes, trk_bboxes, self.iou_threshold
        )
        
        # Update matched trackers with new detections
        for m in matched:
            self.trackers[m[1]].update(det_bboxes[m[0]])
        
        # Create new trackers for unmatched detections
        for i in unmatched_dets:
            trk = KalmanBoxTracker(det_bboxes[i])
            self.trackers.append(trk)
        
        # Prepare output
        tracked_objects = []
        
        for trk in self.trackers:
            # Get current state
            bbox = trk.get_state()
            
            # Only return confirmed tracks (min_hits)
            # And recently updated tracks (max_age)
            if trk.time_since_update < self.max_age and (trk.hits >= self.min_hits or self.frame_count <= self.min_hits):
                # Add confidence from original detection if matched
                confidence = 0.0
                for m in matched:
                    if self.trackers.index(trk) == m[1]:
                        confidence = detections[m[0]]['confidence']
                        break
                
                tracked_obj = {
                    'id': trk.id,
                    'bbox': bbox,
                    'confidence': confidence,
                    'age': trk.age,
                    'hits': trk.hits,
                    'center': (int(bbox[0] + bbox[2]/2), int(bbox[1] + bbox[3]/2))
                }
                tracked_objects.append(tracked_obj)
        
        # Remove dead tracks
        self.trackers = [t for t in self.trackers if t.time_since_update < self.max_age]
        
        return tracked_objects
    
    def get_track_count(self):
        """Get current number of active tracks."""
        return len(self.trackers)
    
    def reset(self):
        """Reset tracker (clear all tracks)."""
        self.trackers = []
        self.frame_count = 0
        KalmanBoxTracker.count = 0


# ==================== TESTING CODE ====================

def test_tracker_with_webcam():
    """
    Test the person tracker with webcam.
    
    This demo shows tracking in action:
    - Each person gets a unique ID
    - IDs persist across frames
    - Shows track age and hits
    """
    print("\n" + "="*60)
    print("TESTING PERSON TRACKER WITH WEBCAM")
    print("="*60)
    print("Press 'q' to quit")
    print("Press 'r' to reset tracker")
    print("="*60 + "\n")
    
    # Import required modules
    sys.path.append(str(Path(__file__).parent.parent))
    from detection.person_detector import PersonDetector
    from utils.video_handler import VideoHandler
    import cv2
    
    # Initialize
    detector = PersonDetector()
    tracker = PersonTracker(max_age=30, min_hits=3, iou_threshold=0.3)
    video = VideoHandler(use_webcam=True)
    
    # Colors for different IDs (for visualization)
    colors = [
        (255, 0, 0), (0, 255, 0), (0, 0, 255),
        (255, 255, 0), (255, 0, 255), (0, 255, 255),
        (128, 0, 0), (0, 128, 0), (0, 0, 128),
        (128, 128, 0), (128, 0, 128), (0, 128, 128)
    ]
    
    frame_count = 0
    
    try:
        while True:
            ret, frame = video.read_frame()
            if not ret:
                break
            
            frame_count += 1
            
            # Detect people
            detections, _ = detector.detect(frame)
            
            # Update tracker
            tracked_objects = tracker.update(detections)
            
            # Draw tracked objects
            for obj in tracked_objects:
                x, y, w, h = [int(v) for v in obj['bbox']]
                track_id = obj['id']
                confidence = obj['confidence']
                
                # Get color for this ID
                color = colors[track_id % len(colors)]
                
                # Draw bounding box
                cv2.rectangle(frame, (x, y), (x + w, y + h), color, 3)
                
                # Draw filled rectangle for label background
                label = f"ID:{track_id}"
                (label_w, label_h), baseline = cv2.getTextSize(
                    label, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2
                )
                cv2.rectangle(frame, (x, y - label_h - 10), 
                            (x + label_w, y), color, -1)
                
                # Draw ID text
                cv2.putText(frame, label, (x, y - 5),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                
                # Draw center point
                cx, cy = obj['center']
                cv2.circle(frame, (cx, cy), 5, color, -1)
            
            # Draw info
            info_text = f"Frame: {frame_count} | Tracks: {len(tracked_objects)} | Total IDs: {KalmanBoxTracker.count}"
            cv2.putText(frame, info_text, (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            # Display
            cv2.imshow("Person Tracking - Press 'q' to quit, 'r' to reset", frame)
            
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                print("\n✅ User pressed 'q'. Exiting...")
                break
            elif key == ord('r'):
                print("\n🔄 Resetting tracker...")
                tracker.reset()
    
    except KeyboardInterrupt:
        print("\n✅ Interrupted by user")
    
    finally:
        video.release()
        cv2.destroyAllWindows()
        print(f"\n✅ Test completed. Processed {frame_count} frames.")
        print(f"Total unique IDs assigned: {KalmanBoxTracker.count}")


if __name__ == "__main__":
    """
    Run this file to test the tracker with webcam.
    
    Usage:
        python tracker.py
    """
    test_tracker_with_webcam()
