# Smart Retail Analytics — IEEE Paper Codebase Analysis

**Project:** Smart Retail Analytics using Computer Vision  
**Codebase Root:** `d:\OneDrive\Desktop\Smart-Retail-Analytics-using-Computer-Vision`  
**Analysis Date:** 2026-03-29

---

## 1. System Architecture

### Top-Level Structure
```
Smart-Retail-Analytics-using-Computer-Vision/
├── main.py                    # CLI entry point & orchestrator (1,107 lines)
├── yolov8n.pt                 # Bundled model weights (~6.5 MB)
├── src/
│   ├── config.py              # Centralized configuration (172 lines)
│   ├── detection/
│   │   └── person_detector.py # YOLOv8 inference wrapper (553 lines)
│   ├── tracking/
│   │   └── tracker.py         # SORT algorithm (541 lines)
│   ├── analytics/
│   │   ├── occupancy_tracker.py    # Zone-based occupancy (301 lines)
│   │   ├── section_analyzer.py     # Multi-section spatial analytics (293 lines)
│   │   ├── heatmap_generator.py    # Density heatmap (263 lines)
│   │   ├── footfall_counter.py     # Line-based footfall (1,163 lines, deprecated)
│   │   └── dwell_time_tracker.py   # (stub file — empty, 0 bytes)
│   └── utils/
│       ├── video_handler.py        # I/O abstraction (VideoHandler, VideoWriter)
│       ├── zone_selector.py        # Interactive polygon zone tool (263 lines)
│       └── multi_section_selector.py # Multi-zone interactive tool
├── zones/                     # Persisted zone JSON files per video
├── sections/                  # Persisted section JSON files per video
└── outputs/
    ├── processed_videos/      # Annotated output MP4 files
    ├── heatmaps/              # Standalone heatmap JPEGs
    └── reports/logs/          # occupancy_log.csv, section_analysis.csv, footfall_log.csv
```

### What [main.py](file:///d:/OneDrive/Desktop/Smart-Retail-Analytics-using-Computer-Vision/main.py) Orchestrates

[main.py](file:///d:/OneDrive/Desktop/Smart-Retail-Analytics-using-Computer-Vision/main.py) defines five distinct run-modes dispatched by `argparse` flags:

| CLI Flag Combination | Run Function | Phase |
|---|---|---|
| `--webcam` | [run_webcam_demo()](file:///d:/OneDrive/Desktop/Smart-Retail-Analytics-using-Computer-Vision/main.py#280-373) | Phase 3 |
| `--video` | [run_video_analysis()](file:///d:/OneDrive/Desktop/Smart-Retail-Analytics-using-Computer-Vision/main.py#375-462) | Phase 3 |
| `--video --footfall` | [run_footfall_video()](file:///d:/OneDrive/Desktop/Smart-Retail-Analytics-using-Computer-Vision/main.py#180-278) | Phase 4 (deprecated) |
| `--video --occupancy` | [run_occupancy_video()](file:///d:/OneDrive/Desktop/Smart-Retail-Analytics-using-Computer-Vision/main.py#464-630) | Phase 4 |
| `--video --analytics` | [run_complete_analytics()](file:///d:/OneDrive/Desktop/Smart-Retail-Analytics-using-Computer-Vision/main.py#762-1024) | Phase 5 |

The **master pipeline** ([run_complete_analytics](file:///d:/OneDrive/Desktop/Smart-Retail-Analytics-using-Computer-Vision/main.py#762-1024)) follows this frame loop:
1. `detector.detect(frame)` → raw YOLO detections
2. `tracker.update(detections)` → tracked objects with persistent IDs
3. `occupancy_tracker.update(tracked_objects, frame_count)` → zone-level occupancy
4. `section_analyzer.update(tracked_objects, frame_count)` → per-section analytics
5. `heatmap_gen.add_positions(people_inside_store)` → density accumulation
6. `heatmap_gen.generate_heatmap_overlay(frame, alpha=0.3)` → real-time heatmap overlay
7. `writer.write_frame(frame)` → output video

---

## 2. Detection Pipeline ([person_detector.py](file:///d:/OneDrive/Desktop/Smart-Retail-Analytics-using-Computer-Vision/src/detection/person_detector.py))

### Model
- **Model:** YOLOv8n (nano) loaded via `ultralytics.YOLO`
- **Weights file:** [yolov8n.pt](file:///d:/OneDrive/Desktop/Smart-Retail-Analytics-using-Computer-Vision/yolov8n.pt), stored at `MODELS_DIR` (checked first) or downloaded on demand
- **Device:** CUDA GPU if available (`USE_GPU = True`), CPU fallback

### Inference Call
```python
results = self.model(frame, conf=self.confidence_threshold, verbose=False)
```
- Input: raw BGR NumPy array at 1280x720 (resized by `VideoHandler`)
- `conf=0.25` passed directly to ultralytics; applied internally during NMS
- `verbose=False` suppresses console output

### Key Parameters

| Parameter | Value | Source |
|---|---|---|
| `YOLO_MODEL` | `"yolov8n.pt"` | config.py:49 |
| `CONFIDENCE_THRESHOLD` | `0.25` | config.py:53 |
| `IOU_THRESHOLD` (NMS) | `0.45` | config.py:55 |
| `PERSON_CLASS_ID` | `0` (COCO "person") | config.py:56 |

> **Note:** `IOU_THRESHOLD = 0.45` is defined in config but NOT explicitly forwarded to the `.model()` call. Ultralytics uses its own default NMS IOU (0.7) unless `iou=` is passed. This is a subtle discrepancy between config intent and actual inference behavior.

### Post-Processing — [_parse_results(result)](file:///d:/OneDrive/Desktop/Smart-Retail-Analytics-using-Computer-Vision/src/detection/person_detector.py#175-234)
1. Iterates `result.boxes`
2. For each box: reads `box.cls[0]` — filters on `class_id == 0` (person only)
3. Reads `box.conf[0]` and `box.xyxy[0]` (GPU tensor → `.cpu().numpy()`)
4. Converts [(x1, y1, x2, y2)](file:///d:/OneDrive/Desktop/Smart-Retail-Analytics-using-Computer-Vision/main.py#1026-1103) to [(x, y, width, height)](file:///d:/OneDrive/Desktop/Smart-Retail-Analytics-using-Computer-Vision/main.py#1026-1103) format
5. Computes `center_x = x + w/2`, `center_y = y + h/2`
6. Returns list of dicts: `{'bbox': (x,y,w,h), 'confidence': float, 'class': 0, 'class_name': 'person', 'center': (cx,cy)}`

### Visualization Color Code
- Confidence > 0.80 → Green [(0,255,0)](file:///d:/OneDrive/Desktop/Smart-Retail-Analytics-using-Computer-Vision/main.py#1026-1103)
- Confidence > 0.60 → Yellow [(0,255,255)](file:///d:/OneDrive/Desktop/Smart-Retail-Analytics-using-Computer-Vision/main.py#1026-1103)
- Confidence <= 0.60 → Orange [(0,165,255)](file:///d:/OneDrive/Desktop/Smart-Retail-Analytics-using-Computer-Vision/main.py#1026-1103)

---

## 3. Tracking Algorithm ([tracker.py](file:///d:/OneDrive/Desktop/Smart-Retail-Analytics-using-Computer-Vision/src/tracking/tracker.py))

### Algorithm: SORT (Simple Online and Realtime Tracking)
Reference: Alex Bewley et al. Uses:
- `filterpy.kalman.KalmanFilter` for state estimation
- `scipy.optimize.linear_sum_assignment` (Hungarian algorithm) for data association
- IoU-based cost matrix

### [KalmanBoxTracker](file:///d:/OneDrive/Desktop/Smart-Retail-Analytics-using-Computer-Vision/src/tracking/tracker.py#33-196) — Per-Target Kalman Filter

**State vector (dim_x=7):** `[x, y, s, r, vx, vy, vs]`
- `x, y` — bounding box center
- `s` — scale (area = w x h)
- `r` — aspect ratio (w/h), assumed constant
- `vx, vy, vs` — corresponding velocities

**Measurement vector (dim_z=4):** `[x, y, s, r]` — only position/size are observed

**State Transition Matrix F:**
```
F = [[1,0,0,0,1,0,0],   # x' = x + vx
     [0,1,0,0,0,1,0],   # y' = y + vy
     [0,0,1,0,0,0,1],   # s' = s + vs
     [0,0,0,1,0,0,0],   # r' = r (constant)
     [0,0,0,0,1,0,0],   # vx' = vx
     [0,0,0,0,0,1,0],   # vy' = vy
     [0,0,0,0,0,0,1]]   # vs' = vs
```

**Measurement Matrix H:** Identity for first 4 rows (observes x, y, s, r)

**Noise Covariance Parameters:**

| Matrix | Modification | Effective Value | Purpose |
|---|---|---|---|
| `R[2:, 2:]` | `*= 0.5` | Halved | Trust measurements MORE (faster response) |
| `P[4:, 4:]` | `*= 1000.0` | 1000x | High initial velocity uncertainty |
| `P` | `*= 10.0` | 10x overall | High initial position uncertainty |
| `Q[-1,-1]` | `*= 0.2` | 0.2x | Allow scale velocity changes |
| `Q[4:,4:]` | `*= 0.2` | 0.2x | Allow position velocity changes |

These are explicitly tuned for **real-time retail tracking** responsiveness over smoothness (comments in code state "DOUBLED from 0.1 to 0.2 for real-time responsiveness").

### Coordinate Conversion
- [_bbox_to_z(bbox)](file:///d:/OneDrive/Desktop/Smart-Retail-Analytics-using-Computer-Vision/src/tracking/tracker.py#168-182): [(x,y,w,h)](file:///d:/OneDrive/Desktop/Smart-Retail-Analytics-using-Computer-Vision/main.py#1026-1103) → [(cx, cy, s=w*h, r=w/h)](file:///d:/OneDrive/Desktop/Smart-Retail-Analytics-using-Computer-Vision/main.py#1026-1103)
- [_z_to_bbox(z)](file:///d:/OneDrive/Desktop/Smart-Retail-Analytics-using-Computer-Vision/src/tracking/tracker.py#183-196): [(cx,cy,s,r)](file:///d:/OneDrive/Desktop/Smart-Retail-Analytics-using-Computer-Vision/main.py#1026-1103) → `w=sqrt(s*r), h=s/w, x=cx-w/2, y=cy-h/2`

### [PersonTracker](file:///d:/OneDrive/Desktop/Smart-Retail-Analytics-using-Computer-Vision/src/tracking/tracker.py#295-424) — Multi-Target Management

**Init parameters (Phase 5 master pipeline):**
```python
PersonTracker(max_age=MAX_DISAPPEARED, min_hits=3, iou_threshold=0.3)
# MAX_DISAPPEARED = 20  (config.py:63)
```

| Parameter | Value | Meaning |
|---|---|---|
| `max_age` | 20 frames | Track deleted after 20 consecutive frames without a match |
| `min_hits` | 3 | Track must match 3 times before appearing in output (suppresses flickering) |
| `iou_threshold` | 0.3 | Minimum IoU for a detection-to-track assignment to be accepted |

**Per-frame [update()](file:///d:/OneDrive/Desktop/Smart-Retail-Analytics-using-Computer-Vision/src/tracking/tracker.py#116-133) logic:**
1. Convert detections to NumPy array of bboxes
2. Call [predict()](file:///d:/OneDrive/Desktop/Smart-Retail-Analytics-using-Computer-Vision/src/tracking/tracker.py#134-158) on all [KalmanBoxTracker](file:///d:/OneDrive/Desktop/Smart-Retail-Analytics-using-Computer-Vision/src/tracking/tracker.py#33-196) instances (advance Kalman state)
3. Remove trackers with NaN in predicted state
4. Call [associate_detections_to_trackers(det_bboxes, trk_bboxes, iou_threshold=0.3)](file:///d:/OneDrive/Desktop/Smart-Retail-Analytics-using-Computer-Vision/src/tracking/tracker.py#239-293)
5. Matched trackers: call `kf.update(measurement)` (Kalman correction step)
6. Unmatched detections: spawn new [KalmanBoxTracker](file:///d:/OneDrive/Desktop/Smart-Retail-Analytics-using-Computer-Vision/src/tracking/tracker.py#33-196), increment `KalmanBoxTracker.count`
7. Unmatched trackers: `time_since_update` increments; deleted when >= `max_age`
8. Output: only tracks where `hits >= min_hits` AND `time_since_update < max_age`

### Hungarian Assignment — [associate_detections_to_trackers()](file:///d:/OneDrive/Desktop/Smart-Retail-Analytics-using-Computer-Vision/src/tracking/tracker.py#239-293)
```python
iou_matrix = iou_batch(detections, trackers)          # M x N matrix
cost_matrix = 1 - iou_matrix
row_idx, col_idx = linear_sum_assignment(cost_matrix) # Scipy Hungarian
# Keep only pairs with iou_matrix[row,col] >= 0.3
```
IoU: `intersection / (area1 + area2 - intersection)` via NumPy broadcasting on XYWH arrays.

### Track ID Management
- `KalmanBoxTracker.count` is a **class-level counter**, incremented on each new instantiation
- IDs are **monotonically increasing integers** starting from 0
- IDs are never reused within a session; [reset()](file:///d:/OneDrive/Desktop/Smart-Retail-Analytics-using-Computer-Vision/src/analytics/footfall_counter.py#971-992) resets [count](file:///d:/OneDrive/Desktop/Smart-Retail-Analytics-using-Computer-Vision/src/tracking/tracker.py#415-418) to 0

---

## 4. Zone & Section Logic

### Polygon Zone Definition — [ZoneSelector](file:///d:/OneDrive/Desktop/Smart-Retail-Analytics-using-Computer-Vision/src/utils/zone_selector.py#17-263)
- **Interactive:** User left-clicks >= 3 points on the first video frame; right-click completes
- **Persistence:** Saved to `zones/{video_stem}_zone.json`:
  ```json
  {"video": "path/to/video.mp4", "points": [[x,y], ...], "num_points": N}
  ```
- **Load on re-run:** `ZoneSelector.load_zone(video_path)` checks for JSON; if found, skips UI

### Point-in-Polygon Test — `ZoneSelector.point_in_polygon()`
```python
poly_np = np.array(polygon, np.int32)
result = cv2.pointPolygonTest(poly_np, point, False)
return result >= 0   # True if inside (+1.0) or on boundary (0.0)
```
- `measureDist=False` — returns sign only, NOT Euclidean distance
- Returns `+1.0` inside, `-1.0` outside, `0.0` on edge
- Called every frame for every tracked person in both [OccupancyTracker](file:///d:/OneDrive/Desktop/Smart-Retail-Analytics-using-Computer-Vision/src/analytics/occupancy_tracker.py#24-301) and [SectionAnalyzer](file:///d:/OneDrive/Desktop/Smart-Retail-Analytics-using-Computer-Vision/src/analytics/section_analyzer.py#29-293)

### `OccupancyTracker.update()` Entry/Exit Logic
1. Build `current_inside` set: track IDs whose center passes [point_in_polygon](file:///d:/OneDrive/Desktop/Smart-Retail-Analytics-using-Computer-Vision/src/utils/zone_selector.py#213-229)
2. **Entries:** IDs in `current_inside` but NOT in previous `self.people_inside`
3. **Exits:** IDs in `self.people_inside` but NOT in `current_inside`
4. **Initial occupancy buffer:** at frame 5, anyone inside is logged as "initial" (stabilization)
5. Logs to `occupancy_log.csv` on entry/exit and every 30 frames ("update" event)

### [SectionAnalyzer](file:///d:/OneDrive/Desktop/Smart-Retail-Analytics-using-Computer-Vision/src/analytics/section_analyzer.py#29-293) — Simultaneous Multi-Section Tracking
- Accepts `sections = [{"name": str, "points": [(x,y),...]}, ...]`
- Persisted to `sections/{video_stem}_sections.json`
- Per-frame [update()](file:///d:/OneDrive/Desktop/Smart-Retail-Analytics-using-Computer-Vision/src/tracking/tracker.py#116-133):
  1. Resets `section_people[name] = set()` for all sections each frame
  2. For each tracked person, checks **each section** independently via [point_in_polygon](file:///d:/OneDrive/Desktop/Smart-Retail-Analytics-using-Computer-Vision/src/utils/zone_selector.py#213-229)
  3. A person CAN appear in multiple sections simultaneously (no exclusivity enforcement)
  4. Updates: `section_occupancy`, `section_peaks`, `section_totals`, `section_history`
  5. Logs "peak" events on new peaks; "update" events every 30 frames

---

## 5. Heatmap Generation ([heatmap_generator.py](file:///d:/OneDrive/Desktop/Smart-Retail-Analytics-using-Computer-Vision/src/analytics/heatmap_generator.py))

### Step-by-Step Pipeline

**Step 1 — Accumulation ([add_positions](file:///d:/OneDrive/Desktop/Smart-Retail-Analytics-using-Computer-Vision/src/analytics/heatmap_generator.py#67-83))**
```python
self.heatmap = np.zeros((frame_height, frame_width), dtype=np.float32)
self.radius = 30        # influence radius in pixels
self.intensity = 1.0    # value per frame per person
# Per tracked person inside store zone:
cv2.circle(self.heatmap, (cx, cy), radius=30, color=1.0, thickness=-1)
```
Filled circle of radius 30 px and intensity 1.0 stamped at each Kalman-filtered centroid.

**Step 2 — Gaussian Blur**
```python
blur_kernel = (25, 25)   # used by master pipeline
blurred = cv2.GaussianBlur(self.heatmap, blur_kernel, 0)
# sigmaX=0: OpenCV infers sigma ~3.7 for k=25
```
Config defines `HEATMAP_BLUR_KERNEL = (15,15)` but [run_complete_analytics](file:///d:/OneDrive/Desktop/Smart-Retail-Analytics-using-Computer-Vision/main.py#762-1024) passes [(25,25)](file:///d:/OneDrive/Desktop/Smart-Retail-Analytics-using-Computer-Vision/main.py#1026-1103).

**Step 3 — Min-Max Normalization**
```python
normalized = cv2.normalize(blurred, None, 0, 255, cv2.NORM_MINMAX)
heatmap_8bit = normalized.astype(np.uint8)
```

**Step 4 — Colorization**
```python
colored_heatmap = cv2.applyColorMap(heatmap_8bit, cv2.COLORMAP_JET)
# 0 → blue (cold/low traffic) ... 255 → red (hot/high traffic)
```

**Step 5 — Masking Zero-Activity Regions**
```python
_, mask = cv2.threshold(heatmap_8bit, 10, 255, cv2.THRESH_BINARY)
mask_3ch = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)
masked_heatmap = cv2.bitwise_and(colored_heatmap, mask_3ch)
```
Prevents COLORMAP_JET's cold blue from flooding zero-activity areas.

**Step 6 — Alpha Blending**
```python
# Real-time overlay (alpha=0.3, master pipeline)
overlay = cv2.addWeighted(frame, 0.7, masked_heatmap, 0.3, 0)
# Saved standalone JPEG: rendered on black canvas with legend strip
```

**Hotspot Detection ([get_hotspots](file:///d:/OneDrive/Desktop/Smart-Retail-Analytics-using-Computer-Vision/src/analytics/heatmap_generator.py#171-201))**
```python
# threshold=0.7, min_area=500 px^2
_, binary = cv2.threshold(normalized_0_1, 0.7, 1, cv2.THRESH_BINARY)
contours = cv2.findContours(binary_8bit, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
hotspots = [c for c in contours if cv2.contourArea(c) >= 500]
```

---

## 6. Dwell Time & Footfall

### Dwell Time
**[dwell_time_tracker.py](file:///d:/OneDrive/Desktop/Smart-Retail-Analytics-using-Computer-Vision/src/analytics/dwell_time_tracker.py) is a zero-byte stub file.** Dwell time tracking is configured but unimplemented:
- `MIN_DWELL_TIME = 5 s` (config.py:110)
- `MAX_DWELL_TIME = 600 s` (config.py:111)
- `SUSPICIOUS_DWELL_TIME = 120 s` (config.py:118)

### Footfall Counter ([footfall_counter.py](file:///d:/OneDrive/Desktop/Smart-Retail-Analytics-using-Computer-Vision/src/analytics/footfall_counter.py)) — Line-Based (Deprecated)

Implements a **virtual line crossing** approach, superseded by [OccupancyTracker](file:///d:/OneDrive/Desktop/Smart-Retail-Analytics-using-Computer-Vision/src/analytics/occupancy_tracker.py#24-301).

**Key Data Structures:**
```python
# deque maxlen = MIN_FRAMES_FOR_DIRECTION * 2 = 2*2 = 4 positions per track
self.track_history = defaultdict(lambda: deque(maxlen=4))
self.counted_entries = set()  # prevents double-counting entries
self.counted_exits = set()    # prevents double-counting exits
self.people_inside = set()    # current occupants
```

**Line Configuration:**
- `ENTRANCE_LINE_ORIENTATION = 'vertical'` (config.py:88)
- `ENTRANCE_LINE_POSITION = 0.35` → X = 35% of frame width (config.py:89)
- `REVERSE_ENTRY_DIRECTION = True` → flips entry/exit direction (config.py:90)
- `CROSSING_BUFFER = 1` pixel minimum delta to confirm crossing (config.py:93)

**[_check_line_crossing()](file:///d:/OneDrive/Desktop/Smart-Retail-Analytics-using-Computer-Vision/src/analytics/footfall_counter.py#317-456) Core Algorithm:**
1. Get position history (deque of [(pos, frame_num)](file:///d:/OneDrive/Desktop/Smart-Retail-Analytics-using-Computer-Vision/main.py#1026-1103))
2. Need `len(history) >= 2` to determine direction
3. Positive crossing: `prev_pos < line_pos AND current_pos > line_pos` AND `|delta| > 1`
4. Negative crossing: `prev_pos > line_pos AND current_pos < line_pos` AND `|delta| > 1`
5. With `REVERSE_ENTRY_DIRECTION=True`: positive=EXIT, negative=ENTRY
6. Single event per track ID enforced by `counted_entries`/`counted_exits` sets

**Zone-Based Entry/Exit (Recommended — [OccupancyTracker](file:///d:/OneDrive/Desktop/Smart-Retail-Analytics-using-Computer-Vision/src/analytics/occupancy_tracker.py#24-301)):**
- Entry: track ID in `current_inside` but not in previous `self.people_inside` (set difference)
- Exit: track ID in `self.people_inside` but not in `current_inside`
- Handles re-entry correctly (purely spatial, no "counted" set blocks)

---

## 7. Output Pipeline

### Processed Videos
- Named: `{analytics|occupancy|footfall|tracked}_{input_video_name}.mp4`
- Saved to `outputs/processed_videos/`
- Encoded with `cv2.VideoWriter_fourcc(*'mp4v')` at original video FPS

### Heatmap Images
- Saved to `outputs/heatmaps/heatmap_{video_stem}.jpg`
- Includes 80 px legend strip with "Low / Medium / High" label using COLORMAP_JET gradient

### CSV Log Files (all in `outputs/reports/logs/`)

**`occupancy_log.csv`** — `OccupancyTracker`:

| Field | Description |
|---|---|
| `timestamp` | `YYYY-MM-DD HH:MM:SS` wall-clock |
| `frame` | Frame number |
| `occupancy` | Current inside-zone count |
| `max_occupancy` | Running session peak |
| `event` | `entry`, `exit`, `initial`, or `update` |
| `track_id` | Track ID (blank for "update" events) |

**`section_analysis.csv`** — `SectionAnalyzer`:

| Field | Description |
|---|---|
| `timestamp` | Wall-clock |
| `frame` | Frame number |
| `section` | Section name string |
| `occupancy` | Current count in section |
| `peak` | Section peak occupancy |
| `event` | `peak` or `update` |
| `track_ids` | Pipe-separated IDs in section |

**`footfall_log.csv`** — `FootfallCounter` (deprecated):

| Field | Description |
|---|---|
| `track_id` | Person track ID |
| `event_type` | `entry` or `exit` |
| `timestamp` | Wall-clock |
| `frame` | Frame number |
| `position_x` | X pixel coordinate of line crossing |
| `position_y` | Y pixel coordinate of line crossing |

---

## 8. Performance & Configuration

### Key `config.py` Parameters

| Parameter | Value | Notes |
|---|---|---|
| `YOLO_MODEL` | `"yolov8n.pt"` | Nano — fastest, ~3.2M params |
| `CONFIDENCE_THRESHOLD` | `0.25` | Lowered from 0.35 for faster response |
| `IOU_THRESHOLD` | `0.45` | NMS config (not forwarded to inference call) |
| `PROCESS_EVERY_N_FRAMES` | `1` | No frame skipping |
| `RESIZE_WIDTH / HEIGHT` | `1280 x 720` | Processing resolution |
| `OUTPUT_VIDEO_FPS` | `30` | |
| `MAX_DISAPPEARED` | `20` | Tracker max_age |
| `MAX_DISTANCE` | `250` | Centroid distance config (not used in SORT tracking) |
| `HEATMAP_BLUR_KERNEL` | `(15,15)` | Config; overridden to `(25,25)` in master pipeline |
| `HEATMAP_ALPHA` | `0.6` | Config; overridden to `0.3` in master pipeline |
| `MIN_DWELL_TIME` | `5 s` | Defined but not implemented |
| `MAX_OCCUPANCY_LIMIT` | `50` | Alert threshold |
| `USE_GPU` | `True` | CUDA if available |
| `NUM_THREADS` | `4` | CPU threads |

### Test Video Context (retail.mp4)
- 781 frames at 30 FPS (~26 seconds), native 1080p, processed at 1280x720
- Hardware: Intel i7 CPU
- No exact measured FPS or detection accuracy numbers exist as hardcoded values in the codebase; no CSV output files were present in `outputs/reports/` at time of analysis

---

## 9. Key Algorithmic Innovations

### A. Polygon Zone vs. Virtual Line
The evolution from `FootfallCounter` (line-crossing) to `OccupancyTracker` (polygon containment) is the central design innovation:
- Lines require perpendicular camera-to-door alignment
- Polygon zones work with **any camera angle** (ceiling-mounted, oblique, fisheye)
- `cv2.pointPolygonTest` is O(n) in polygon vertices — extremely fast for typical 4–8 vertex zones
- Zone JSON persistence enables reproducible multi-session analysis

### B. Single-Loop Unified Pipeline
`run_complete_analytics()` integrates 5 subsystems (YOLO + SORT + OccupancyTracker + SectionAnalyzer + HeatmapGenerator) in **one frame loop** without inter-process communication or buffering. This bounds max latency to one frame's processing time.

### C. Zone-Filtered Heatmap Accumulation
```python
people_inside_store = [obj for obj in tracked_objects
                       if ZoneSelector.point_in_polygon(obj['center'], store_zone)]
heatmap_gen.add_positions(people_inside_store)
```
Only **Kalman-filtered centroids of in-zone persons** contribute to the heatmap — eliminating entrance-noise and outside-zone movement from density maps.

### D. Dual Footfall Paradigm
Two parallel counting strategies are maintained simultaneously:
1. **`FootfallCounter`** — virtual line, stateful, one-directional, per-ID cross-count
2. **`OccupancyTracker`** — spatial containment, stateless per-frame, handles re-entry

### E. Occlusion Tolerance via Kalman Prediction
`max_age=20` means tracks survive occlusions up to ~0.67 s at 30 FPS through Kalman extrapolation — preventing false exits/re-entries in crowd scenarios.

---

## 10. Limitations & Edge Cases

### A. Dwell Time Unimplemented
`dwell_time_tracker.py` is a zero-byte file. All config parameters for dwell time exist but are entirely unused in the running pipeline.

### B. No Appearance Features (SORT vs. DeepSORT)
SORT has no re-ID / appearance descriptor. Persons who cross paths may swap IDs after occlusion. Config claims `TRACKING_METHOD = "deepsort"` but the actual implementation is the custom SORT class in `tracker.py`.

### C. Class-Level ID Counter Reset Risk
`KalmanBoxTracker.count` is class-level. Calling `PersonTracker.reset()` resets it to 0, creating ID collisions and corrupting CSV analytics logs in interactive sessions.

### D. Camera-Fixed Zone Coordinates
Polygon points are in pixel space on the first frame. Camera movement, zoom, or video replacement requires manual zone re-annotation; no automatic calibration or homography correction exists.

### E. Single Global Heatmap
Heatmap accumulation uses one store-level zone mask, not per-section. Section boundaries do not gate heatmap stamping.

### F. No Image Pre-processing Before YOLO
No CLAHE, histogram equalization, or white-balance correction before inference. YOLOv8n at confidence 0.25 will produce false positives under poor retail lighting (glass reflections, strong shadows, backlight).

### G. One-Way Footfall Double-Count Prevention
`counted_entries`/`counted_exits` sets grow indefinitely per session. A person who exits and re-enters will NOT be counted as a re-entry. The zone-based approach handles this correctly via set membership.

### H. Overlapping Section Inflation
`SectionAnalyzer` allows polygon overlaps. A person in an overlapping region is counted in ALL overlapping sections simultaneously, inflating per-section totals.

### I. CPU Performance Ceiling
YOLOv8n at 1280x720 on Intel i7 achieves approximately 20–30 FPS. With full analytics pipeline (5 subsystems), throughput may drop below real-time 30 FPS without GPU acceleration.

---

## Quick Reference: All Numeric Parameters

| Parameter | Value | File:Line |
|---|---|---|
| YOLO confidence threshold | 0.25 | config.py:53 |
| YOLO NMS IOU threshold | 0.45 | config.py:55 |
| COCO person class ID | 0 | config.py:56 |
| Frame processing stride | 1 (every frame) | config.py:37 |
| Resize dimensions | 1280x720 | config.py:39-40 |
| Kalman R[2:,2:] scaling | x0.5 | tracker.py:91 |
| Kalman P[4:,4:] scaling | x1000.0 | tracker.py:96 |
| Kalman P overall scaling | x10.0 | tracker.py:97 |
| Kalman Q[-1,-1] scaling | x0.2 | tracker.py:101 |
| Kalman Q[4:,4:] scaling | x0.2 | tracker.py:102 |
| Track max_age | 20 frames | config.py:63 |
| Track min_hits | 3 frames | main.py:790 |
| Track IOU threshold | 0.3 | tracker.py:239 |
| Zone fill alpha (overlay) | 0.15 | occupancy_tracker.py:205 |
| Heatmap influence radius | 30 px | heatmap_generator.py:62 |
| Heatmap Gaussian kernel | (25,25) | main.py:904 |
| Heatmap alpha (live overlay) | 0.3 | main.py:983 |
| Heatmap activity mask threshold | 10 (uint8) | heatmap_generator.py:109 |
| Heatmap hotspot threshold | 0.7 (70% of max) | heatmap_generator.py:171 |
| Hotspot min contour area | 500 px^2 | heatmap_generator.py:171 |
| Occupancy log frequency | every 30 frames | occupancy_tracker.py:180 |
| Section log frequency | every 30 frames | section_analyzer.py:141 |
| Initial occupancy buffer | frame 5 | occupancy_tracker.py:159 |
| Footfall line position | 35% from left | config.py:89 |
| Footfall crossing buffer | 1 px | config.py:93 |
| Min frames for direction | 2 | config.py:94 |
| Min dwell time (unused) | 5 s | config.py:110 |
| Max dwell time (unused) | 600 s | config.py:111 |
| Suspicious dwell time (unused) | 120 s | config.py:118 |
| Max occupancy alert limit | 50 persons | config.py:102 |
