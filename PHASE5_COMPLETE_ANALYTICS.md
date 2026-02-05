# 📊 PHASE 5: COMPLETE RETAIL ANALYTICS

## 🎯 Overview

**Phase 5** is the ultimate retail analytics solution that combines everything into a single, comprehensive analysis system. It builds upon the reliable zone-based occupancy tracking from Phase 4 and adds advanced multi-section analysis and heatmap visualization.

---

## ✨ What's Included

```
┌─────────────────────────────────────────────────────────────┐
│              PHASE 5: COMPLETE ANALYTICS                    │
│  Single Command = Complete Retail Insights                 │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│  1️⃣  OVERALL OCCUPANCY (from Phase 4)                      │
│     ✅ Track total people in store                          │
│     ✅ Peak occupancy monitoring                            │
│     ✅ Entry/exit detection (zone boundary crossing)        │
│     ✅ Real-time count display                              │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│  2️⃣  SECTION-WISE ANALYSIS (NEW!)                          │
│     ✅ Define multiple sections (Electronics, Clothing...)  │
│     ✅ Track occupancy per section                          │
│     ✅ Peak traffic per section                             │
│     ✅ Section comparison analytics                         │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│  3️⃣  HEATMAP VISUALIZATION (NEW!)                          │
│     🔴 RED = High traffic areas (hot spots)                 │
│     🟡 YELLOW = Medium traffic zones                        │
│     🟢 GREEN/BLUE = Low traffic areas (cold spots)          │
│     ✅ Overlaid on video in real-time                       │
│     ✅ Standalone heatmap image export                      │
└─────────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### **Phase 4: Occupancy Only (Simple)**
```powershell
python main.py --video "data/input_videos/retail.mp4" --occupancy
```

**What you get:**
- Overall store occupancy tracking
- Peak occupancy count
- Green boxes (inside store) / Red boxes (outside store)
- Output: `occupancy_retail.mp4`

---

### **Phase 5: Complete Analytics (Recommended) ⭐**
```powershell
python main.py --video "data/input_videos/retail.mp4" --analytics
```

**What you get:**
- Everything from Phase 4 PLUS:
- Section-wise occupancy (Electronics: 3, Clothing: 5, etc.)
- Heatmap overlay showing crowd density
- Comprehensive analytics report
- Output: `analytics_retail.mp4` + `heatmap_retail.jpg`

---

## 📋 Step-by-Step Usage

### **First Time Setup (Phase 5):**

#### **Step 1: Run Command**
```powershell
python main.py --video "data/input_videos/retail.mp4" --analytics
```

#### **Step 2: Define Store Boundary**
A window will open showing the first frame of your video.

**Instructions:**
- **Left-click** to add points around the store boundary
- **Right-click** when done (minimum 3 points)
- This defines the overall store area

#### **Step 3: Define Sections**
You'll be prompted in the console:

```
Enter name for Section 1 (or 'q' to finish): Electronics
```

**For each section:**
1. Type section name (e.g., "Electronics") and press Enter
2. Window opens - left-click to add boundary points
3. Right-click when done
4. Repeat for next section (Clothing, Groceries, etc.)
5. Type 'q' when all sections are defined

**Example Sections:**
- Electronics
- Clothing
- Groceries
- Checkout
- Entry Area
- etc.

#### **Step 4: Processing Begins**
- System processes entire video
- Shows progress: `Processed 300/776 frames (38.7%) | Occupancy: 8`
- Generates analytics video with all overlays

#### **Step 5: View Results**
```
✅ Processing complete!
📹 Analytics video saved: outputs/processed_videos/analytics_retail.mp4
🔥 Heatmap saved: outputs/heatmaps/heatmap_retail.jpg
📊 Section log: outputs/reports/logs/section_analysis.csv
```

---

### **Second Time (Zones Saved - Interactive Prompts):**

```powershell
python main.py --video "data/input_videos/retail.mp4" --analytics
```

**What happens:**
```
✅ Loaded saved store zone
============================================================
Do you want to REDEFINE store boundary? (yes/no): no
============================================================
✅ Using saved store zone

✅ Loaded 1 saved sections:
   1. electronics
============================================================
Do you want to REDEFINE sections? (yes/no): yes
============================================================
🔄 Redefining sections...

Enter name for Section 1 (or 'q' to finish): Electronics
[Define boundary...]

Enter name for Section 2 (or 'q' to finish): Clothing
[Define boundary...]

Enter name for Section 3 (or 'q' to finish): q
```

**Result:**
- ✅ Can choose to keep or redefine store zone
- ✅ Can choose to keep or redefine sections
- ✅ Interactive - no need to remember flags!
- ✅ Sections overwritten with your new definitions

---

### **Want to Redefine Without Prompts?**

**Option 1: Use flag (skips prompts)**
```powershell
python main.py --video "data/input_videos/retail.mp4" --analytics --redefine-zones
```
- Forces zone AND section reselection
- No interactive prompts
- Goes straight to selection UI

**Option 2: Delete saved files (manual)**
```powershell
Remove-Item zones\retail_zone.json
Remove-Item sections\retail_sections.json
python main.py --video "data/input_videos/retail.mp4" --analytics
```
- Deletes saved configurations
- System treats as first-time run

**Option 3: Interactive prompts (recommended)**
```powershell
python main.py --video "data/input_videos/retail.mp4" --analytics
# Just answer "yes" when prompted to redefine
```
- ✅ Most user-friendly
- ✅ Can choose to keep store zone but redefine sections
- ✅ Or vice versa

---

## 📊 Output Files

### **1. Analytics Video**
**File:** `outputs/processed_videos/analytics_retail.mp4`

**Contains:**
- ✅ Bounding boxes (green=inside store, red=outside)
- ✅ Track IDs for each person
- ✅ Store zone boundary (yellow outline)
- ✅ Section boundaries (multi-colored outlines)
- ✅ Section names with occupancy counts
- ✅ Heatmap overlay (semi-transparent color coding)
- ✅ Overall occupancy stats (top-right corner)
- ✅ Section statistics (bottom-left corner)

**Visual Example:**
```
┌─────────────────────────────────────────────┐
│ Occupancy: 8 | Peak: 12        [TOP-RIGHT] │
│                                             │
│   🟢 ID:5 IN     [Store Zone]              │
│   🟢 ID:7 IN                                │
│                                             │
│   [Electronics: 3]  [Clothing: 5]          │
│                                             │
│   🔴🟡🟢 Heatmap overlay                     │
│                                             │
│ SECTION ANALYTICS:         [BOTTOM-LEFT]   │
│ Electronics: 3 (Peak: 4)                   │
│ Clothing: 5 (Peak: 7)                      │
└─────────────────────────────────────────────┘
```

---

### **2. Heatmap Image**
**File:** `outputs/heatmaps/heatmap_retail.jpg`

**Contains:**
- Full-resolution heatmap
- Color gradient legend (Low → Medium → High)
- Standalone image for presentations/reports

**Color Coding:**
- 🔵 **Blue/Green:** Low traffic (rarely visited)
- 🟡 **Yellow/Orange:** Medium traffic (moderate activity)
- 🔴 **Red:** High traffic (hot spots, popular areas)

---

### **3. Section Analytics Log**
**File:** `outputs/reports/logs/section_analysis.csv`

**Format:**
```csv
timestamp,frame,section,occupancy,peak,event,track_ids
2026-02-05 14:30:15,1,Electronics,2,2,update,5|7
2026-02-05 14:30:16,30,Electronics,3,3,peak,5|7|9
2026-02-05 14:30:16,30,Clothing,5,5,update,1|3|4|8|11
```

**Columns:**
- `timestamp`: Date/time of event
- `frame`: Frame number
- `section`: Section name
- `occupancy`: Current count in that section
- `peak`: Peak count for that section so far
- `event`: Type of event (update, peak)
- `track_ids`: IDs of people in section (pipe-separated)

---

### **4. Occupancy Log** (from Phase 4)
**File:** `outputs/reports/logs/occupancy_log.csv`

Overall store occupancy data (same as Phase 4).

---

## 🎨 Visual Features

### **Color Coding System:**

#### **Person Bounding Boxes:**
| Color | Meaning | Label |
|-------|---------|-------|
| 🟢 Green | Inside store zone | "ID:5 IN" |
| 🔴 Red | Outside store zone | "ID:3 OUT" |

#### **Zone Boundaries:**
| Color | Element |
|-------|---------|
| 🟡 Yellow | Store boundary (main zone) |
| 🔵 Cyan | Section 1 (e.g., Electronics) |
| 🟣 Magenta | Section 2 (e.g., Clothing) |
| 🟠 Orange | Section 3 (e.g., Groceries) |
| ... | (Colors cycle for more sections) |

#### **Heatmap Overlay:**
| Color | Traffic Level |
|-------|---------------|
| 🔴 Red | HIGH - Most popular area |
| 🟡 Yellow | MEDIUM - Moderate traffic |
| 🟢 Green | LOW - Less visited |
| 🔵 Blue | VERY LOW - Rarely visited |

---

## 📈 Statistics Summary

After processing completes, you'll see comprehensive statistics:

```
============================================================
OCCUPANCY TRACKING SUMMARY
============================================================
👥 Current Occupancy:   5
📊 Peak Occupancy:      12
📈 Average Occupancy:   8.3
⏱  Duration:            25.87 seconds
🎬 Total Frames:        776
📋 Log File:            outputs/reports/logs/occupancy_log.csv
============================================================

============================================================
SECTION ANALYTICS SUMMARY
============================================================

📍 Electronics:
   Current Occupancy:  2
   Peak Occupancy:     4
   Average Occupancy:  2.8

📍 Clothing:
   Current Occupancy:  3
   Peak Occupancy:     7
   Average Occupancy:  4.1

📍 Groceries:
   Current Occupancy:  0
   Peak Occupancy:     3
   Average Occupancy:  1.4

📊 Overall:
   Total Current:      5
   Total Peaks Sum:    14
   Frames Processed:   776

📋 Log File: outputs/reports/logs/section_analysis.csv
============================================================

============================================================
HEATMAP ANALYSIS SUMMARY
============================================================
🔥 Frames Accumulated:    776
🔥 Hotspots Identified:   3
🔥 Max Density:           127.50
🔥 Mean Density:          42.30
🔥 Coverage:              35.2%
============================================================
```

---

## 🔧 Advanced Options

### **Redefine Only Store Zone:**
```powershell
python main.py --video retail.mp4 --analytics --redefine-zone
```
- Redraws store boundary only
- Keeps saved sections

### **Redefine Everything:**
```powershell
python main.py --video retail.mp4 --analytics --redefine-zones
```
- Redraws store boundary AND all sections
- Fresh start

### **Process Multiple Videos:**
```powershell
python main.py --video "store1.mp4" --analytics
python main.py --video "store2.mp4" --analytics
```
- Each video saves its own zones/sections
- Automatically loads correct configuration per video

---

## 🎯 Use Cases

### **Retail Store Management:**
- **Overall Occupancy:** Monitor total customer count
- **Section Analysis:** Identify popular departments (e.g., Electronics has 2x traffic vs. Groceries)
- **Heatmaps:** Optimize product placement (move popular items to cold zones)
- **Peak Detection:** Staff scheduling based on busy sections

### **Shopping Mall Analytics:**
- Track foot traffic per store/zone
- Compare performance across different areas
- Identify dead zones for improvement

### **Museum/Exhibition:**
- Monitor visitor distribution across exhibits
- Prevent overcrowding in specific galleries
- Identify most popular exhibits

### **Restaurant/Café:**
- Dining area vs. counter occupancy
- Queue management (checkout section analysis)
- Table turnover insights

---

## 🐛 Troubleshooting

### **Issue: Sections overlapping**
**Solution:** Define non-overlapping sections. A person can be in multiple sections simultaneously if boundaries overlap.

### **Issue: Heatmap not showing**
**Solution:** 
- Heatmap only shows for people INSIDE the store zone
- Increase `alpha` parameter in code for more visible overlay (default: 0.3)

### **Issue: Section names too long**
**Solution:** Use short names like "Elec", "Cloth" instead of "Electronics Department"

### **Issue: Want to remove a section**
**Solution:** 
1. Delete `sections/retail_sections.json`
2. Run with `--redefine-zones`
3. Define only the sections you want

### **Issue: Heatmap colors incorrect**
**Solution:** 
- Blue/Green = LOW traffic (correct, rarely visited)
- Red = HIGH traffic (correct, hot spots)
- This is intentional! Cold colors for cold zones.

---

## 📁 File Structure

```
Smart-Retail-Analytics-using-Computer-Vision/
├── outputs/
│   ├── processed_videos/
│   │   ├── occupancy_retail.mp4        # Phase 4 output
│   │   └── analytics_retail.mp4        # Phase 5 output ⭐
│   ├── heatmaps/
│   │   └── heatmap_retail.jpg          # Standalone heatmap ⭐
│   └── reports/
│       └── logs/
│           ├── occupancy_log.csv       # Overall occupancy
│           └── section_analysis.csv    # Section-wise data ⭐
├── zones/
│   └── retail_zone.json                # Saved store boundary
├── sections/
│   └── retail_sections.json            # Saved sections ⭐
└── main.py                             # Main script
```

---

## 💡 Best Practices

### **Zone Definition:**
1. **Store Boundary:** Draw around the walkable area, not walls
2. **Sections:** Define logical divisions (by product category, area function)
3. **Avoid Tiny Sections:** Minimum ~10% of store area per section
4. **Non-Overlapping:** Keep sections separate for clear analytics

### **Section Naming:**
- ✅ Good: "Electronics", "Clothing", "Checkout"
- ❌ Avoid: "The Electronics Department with TVs and Phones"

### **Multiple Runs:**
- First video: Takes time (zone selection)
- Subsequent runs: Instant (loads saved zones)
- Different videos: Each has own saved configuration

---

## 🔄 Phase 4 vs Phase 5 Comparison

| Feature | Phase 4 (--occupancy) | Phase 5 (--analytics) |
|---------|------------------------|------------------------|
| **Overall Occupancy** | ✅ Yes | ✅ Yes |
| **Peak Tracking** | ✅ Yes | ✅ Yes |
| **Entry/Exit Detection** | ✅ Yes | ✅ Yes |
| **Section Analysis** | ❌ No | ✅ Yes (Multi-section) |
| **Section-wise Peaks** | ❌ No | ✅ Yes |
| **Heatmap Visualization** | ❌ No | ✅ Yes (Real-time overlay) |
| **Hot Spot Detection** | ❌ No | ✅ Yes |
| **Section Comparison** | ❌ No | ✅ Yes |
| **Standalone Heatmap** | ❌ No | ✅ Yes (JPG export) |
| **Setup Time** | Fast (1 zone) | Moderate (1 zone + N sections) |
| **Output Files** | 2 files | 4 files |
| **Use Case** | Simple occupancy | Comprehensive analytics |

**When to use Phase 4:**
- Quick occupancy check
- Single-zone tracking sufficient
- No need for spatial analytics

**When to use Phase 5:**
- Detailed spatial insights needed
- Compare different store areas
- Identify traffic patterns
- Optimize store layout

---

## 🎓 Technical Details

### **Section Detection Algorithm:**
```python
FOR each person:
    person_center = (cx, cy)
    
    FOR each section:
        IF point_in_polygon(person_center, section.points):
            section.occupancy += 1
            section.track_ids.add(person.id)
```

### **Heatmap Generation:**
```python
FOR each frame:
    FOR each person INSIDE store:
        # Add Gaussian blob at person's position
        heatmap[person_y, person_x] += intensity
        
# After all frames:
heatmap_normalized = normalize(heatmap)
heatmap_colored = apply_colormap(heatmap_normalized, COLORMAP_JET)
overlay = blend(video_frame, heatmap_colored, alpha=0.3)
```

### **Performance:**
- Section checking: O(N × M) per frame
  - N = number of people
  - M = number of sections
- Heatmap accumulation: O(N) per frame
- Minimal overhead compared to Phase 4

---

## ⚙️ Configuration

Edit `src/config.py` to customize:

```python
# Heatmap settings
HEATMAP_BLUR_KERNEL = (25, 25)  # Smoothing (higher = smoother)
HEATMAP_ALPHA = 0.3              # Overlay transparency (0.0-1.0)

# Section colors (automatically cycled)
SECTION_COLORS = [
    (255, 0, 255),  # Magenta
    (0, 255, 255),  # Cyan
    # Add more colors for more sections
]

# Logging
ENABLE_OCCUPANCY_LOGGING = True
ENABLE_SECTION_LOGGING = True
```

---

## 🎉 Summary

**Phase 5 gives you the COMPLETE picture:**

✅ **WHO:** How many people (overall occupancy)  
✅ **WHERE:** Which sections they visit (section analysis)  
✅ **PATTERNS:** Traffic density visualization (heatmaps)  
✅ **TRENDS:** Peak times per section (analytics logs)  

**All in ONE command, ONE video output!**

---

## 🚀 Next Steps

1. **Run Phase 5 on your retail video:**
   ```powershell
   python main.py --video "data/input_videos/retail.mp4" --analytics
   ```

2. **Define meaningful sections** (product categories, functional areas)

3. **Analyze outputs:**
   - Watch `analytics_retail.mp4` - see everything live!
   - View `heatmap_retail.jpg` - identify hot/cold zones
   - Check `section_analysis.csv` - detailed data

4. **Make decisions:**
   - Rearrange store layout (move products to hot zones)
   - Optimize staffing (more staff in busy sections)
   - Improve customer flow (address bottlenecks)

---

**🎯 Phase 5 Complete! Smart Retail Analytics at Your Fingertips!** 🎉
