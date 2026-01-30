"""
Configuration file for Smart Retail Analytics System

This file centralizes all configuratLINE_THICKNESS = 3  # Thickness of entrance line
LINE_COLOR_ENTRANCE = (0, 255, 255)  # Yellow/Cyan for entrance line (BGR)
CROSSING_BUFFER = 5  # Pixels buffer to confirm line crossing
MIN_FRAMES_FOR_DIRECTION = 3  # Minimum frames to determine direction

# Debug mode - Set to True to see position tracking (lots of output!)
FOOTFALL_DEBUG_MODE = False  # ← Disabled - Issue identified! Set to True only for troubleshootingtings for the project.
This makes it easy to modify parameters without changing the core code.
"""

import os
from pathlib import Path

# ==================== PROJECT PATHS ====================
# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
MODELS_DIR = PROJECT_ROOT / "models"
OUTPUTS_DIR = PROJECT_ROOT / "outputs"

# Input/Output directories
INPUT_VIDEOS_DIR = DATA_DIR / "input_videos"
SAMPLE_VIDEOS_DIR = DATA_DIR / "sample_videos"
PROCESSED_VIDEOS_DIR = OUTPUTS_DIR / "processed_videos"
HEATMAPS_DIR = OUTPUTS_DIR / "heatmaps"
REPORTS_DIR = OUTPUTS_DIR / "reports"

# ==================== VIDEO PROCESSING ====================
# Video input settings
DEFAULT_VIDEO_PATH = INPUT_VIDEOS_DIR / "test_video.mp4"
WEBCAM_INDEX = 0  # 0 for default webcam

# Frame processing
PROCESS_EVERY_N_FRAMES = 1  # Process every frame (1) for best real-time tracking
                             # Increase to 2-3 only if performance is slow
RESIZE_WIDTH = 1280  # Resize frame width for processing (None to keep original)
RESIZE_HEIGHT = 720  # Resize frame height

# Display settings
DISPLAY_FRAME = True  # Show video while processing
SAVE_OUTPUT_VIDEO = True  # Save processed video
OUTPUT_VIDEO_FPS = 30  # FPS for output video

# ==================== PERSON DETECTION (YOLO) ====================
# Model selection
YOLO_MODEL = "yolov8n.pt"  # Options: yolov8n, yolov8s, yolov8m, yolov8l, yolov8x
                            # 'n' = nano (fastest), 'x' = extra large (most accurate)

# Detection parameters
CONFIDENCE_THRESHOLD = 0.25  # Minimum confidence to detect a person (0.0 - 1.0)
                             # Lowered to 0.25 for faster detection response (was 0.35)
IOU_THRESHOLD = 0.45  # Intersection over Union threshold for NMS
PERSON_CLASS_ID = 0  # COCO dataset class ID for 'person'

# ==================== TRACKING ====================
# Tracking algorithm
TRACKING_METHOD = "deepsort"  # Options: "sort", "deepsort", "bytetrack"

# Tracking parameters - OPTIMIZED FOR REAL-TIME RESPONSIVENESS
MAX_DISAPPEARED = 20  # Max frames to keep track before removing (reduced from 30 for faster response)
MAX_DISTANCE = 250  # Max distance for track association (increased to 250 for very fast movement)

# ==================== ANALYTICS ====================
# Occupancy Tracking (Phase 4 - ZONE-BASED)
# NEW APPROACH: Uses polygon zones instead of line crossing
# More reliable and works with any camera angle!

# Zone-based settings
ENABLE_OCCUPANCY_LOGGING = True  # Log occupancy events to CSV
OCCUPANCY_LOG_FILE = "occupancy_log.csv"

# Visual settings for zone overlay
ZONE_COLOR = (0, 255, 255)  # Yellow (BGR)
ZONE_THICKNESS = 3
ZONE_FILL_ALPHA = 0.15  # Transparency of zone overlay (0=transparent, 1=opaque)

# Person visualization colors
PERSON_INSIDE_COLOR = (0, 255, 0)  # Green = inside zone
PERSON_OUTSIDE_COLOR = (0, 0, 255)  # Red = outside zone

# ==================== LEGACY: LINE-BASED FOOTFALL (DEPRECATED) ====================
# These settings are kept for backward compatibility with --footfall flag
# RECOMMENDED: Use --occupancy flag with zone-based tracking instead!

ENTRANCE_LINE_ORIENTATION = 'vertical'  # 'horizontal' or 'vertical'
ENTRANCE_LINE_POSITION = 0.35  # 0.0 to 1.0 (percentage position)
REVERSE_ENTRY_DIRECTION = True  # Flip entry/exit directions
LINE_THICKNESS = 3
LINE_COLOR_ENTRANCE = (0, 255, 255)  # Yellow (BGR)
CROSSING_BUFFER = 1  # Pixels buffer for line crossing
MIN_FRAMES_FOR_DIRECTION = 2
FOOTFALL_DEBUG_MODE = False  # Set True for detailed crossing logs
INSIDE_ZONE_POSITION = 'left'  # Which side is "inside": 'left', 'right', 'top', 'bottom'
ENABLE_FOOTFALL_LOGGING = True  # Log footfall events to CSV
FOOTFALL_LOG_FILE = "footfall_log.csv"

# Occupancy tracking
ENABLE_OCCUPANCY_TRACKING = True  # Track current people count
MAX_OCCUPANCY_LIMIT = 50  # Maximum allowed occupancy (for alerts)

# Data logging
ENABLE_FOOTFALL_LOGGING = True  # Log all entry/exit events
FOOTFALL_LOG_FILE = "footfall_log.csv"  # CSV file for footfall data
SAVE_LOGS_DIR = REPORTS_DIR / "logs"  # Directory for log files

# Dwell time (in seconds)
MIN_DWELL_TIME = 5  # Minimum time to consider as "dwelled"
MAX_DWELL_TIME = 600  # Maximum reasonable dwell time (10 minutes)

# Heatmap settings
HEATMAP_BLUR_KERNEL = (15, 15)  # Gaussian blur kernel size
HEATMAP_ALPHA = 0.6  # Transparency of heatmap overlay

# Anti-theft thresholds
SUSPICIOUS_DWELL_TIME = 120  # 2 minutes in one spot
ERRATIC_MOVEMENT_THRESHOLD = 100  # Movement pattern complexity threshold

# ==================== REPORTING ====================
# Report generation
REPORT_FREQUENCY = "daily"  # Options: "hourly", "daily", "weekly"
TIME_BINS = ["09:00", "12:00", "15:00", "18:00", "21:00"]  # Hour bins for analysis

# ==================== SYSTEM ====================
# Performance
USE_GPU = True  # Use GPU if available (requires CUDA)
NUM_THREADS = 4  # Number of CPU threads

# Logging
LOG_LEVEL = "INFO"  # Options: DEBUG, INFO, WARNING, ERROR
LOG_FILE = "retail_analytics.log"

# ==================== HELPER FUNCTIONS ====================
def create_directories():
    """Create all necessary directories if they don't exist."""
    directories = [
        INPUT_VIDEOS_DIR,
        SAMPLE_VIDEOS_DIR,
        PROCESSED_VIDEOS_DIR,
        HEATMAPS_DIR,
        REPORTS_DIR,
        REPORTS_DIR / "logs",  # For footfall logs
        MODELS_DIR
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
        print(f"✓ Directory ready: {directory}")

def get_model_path(model_name):
    """Get full path to model file."""
    return MODELS_DIR / model_name

def print_config():
    """Print current configuration (useful for debugging)."""
    print("\n" + "="*50)
    print("SMART RETAIL ANALYTICS - CONFIGURATION")
    print("="*50)
    print(f"Project Root: {PROJECT_ROOT}")
    print(f"YOLO Model: {YOLO_MODEL}")
    print(f"Confidence Threshold: {CONFIDENCE_THRESHOLD}")
    print(f"Use GPU: {USE_GPU}")
    print(f"Process Every N Frames: {PROCESS_EVERY_N_FRAMES}")
    print("="*50 + "\n")

if __name__ == "__main__":
    # Test configuration
    print_config()
    create_directories()
