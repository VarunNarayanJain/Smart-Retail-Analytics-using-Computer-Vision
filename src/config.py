"""
Configuration file for Smart Retail Analytics System

This file centralizes all configuration settings for the project.
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
PROCESS_EVERY_N_FRAMES = 1  # Process every frame (1) or skip frames (2, 3, etc.)
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
CONFIDENCE_THRESHOLD = 0.5  # Minimum confidence to detect a person (0.0 - 1.0)
IOU_THRESHOLD = 0.45  # Intersection over Union threshold for NMS
PERSON_CLASS_ID = 0  # COCO dataset class ID for 'person'

# ==================== TRACKING ====================
# Tracking algorithm
TRACKING_METHOD = "deepsort"  # Options: "sort", "deepsort", "bytetrack"

# Tracking parameters
MAX_DISAPPEARED = 30  # Max frames to keep track before removing
MAX_DISTANCE = 50  # Max distance for track association

# ==================== ANALYTICS ====================
# Footfall counting
ENTRY_LINE_POSITION = 0.2  # Entry line at 20% of frame height (from top)
EXIT_LINE_POSITION = 0.8   # Exit line at 80% of frame height

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
