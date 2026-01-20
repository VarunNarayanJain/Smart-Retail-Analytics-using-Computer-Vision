# 🚀 Setup Guide - Smart Retail Analytics System

This guide will help you set up the development environment step-by-step.

---

## 📋 Prerequisites

- **Python 3.8 or higher** (Python 3.9 or 3.10 recommended)
- **Webcam** (for testing) or sample retail videos
- **8GB RAM minimum** (16GB recommended for YOLO processing)
- **GPU (Optional)**: NVIDIA GPU with CUDA support for faster processing

---

## 🔧 Step 1: Create Virtual Environment

A virtual environment keeps project dependencies isolated.

### Windows (PowerShell):
```powershell
# Navigate to project directory
cd "d:\OneDrive\Desktop\Smart-Retail-Analytics-using-Computer-Vision"

# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# If you get execution policy error, run:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Windows (Command Prompt):
```cmd
python -m venv venv
venv\Scripts\activate.bat
```

### Linux/Mac:
```bash
python3 -m venv venv
source venv/bin/activate
```

You should see `(venv)` in your terminal prompt.

---

## 📦 Step 2: Install Dependencies

```powershell
# Upgrade pip first
python -m pip install --upgrade pip

# Install all required packages
pip install -r requirements.txt
```

This will install:
- OpenCV (computer vision)
- Ultralytics (YOLOv8)
- PyTorch (deep learning)
- NumPy, Pandas (data processing)
- Matplotlib, Seaborn (visualization)

**Note**: Installation may take 5-10 minutes depending on your internet speed.

---

## 🧪 Step 3: Test Your Setup

### Test 1: Check Python and Packages
```powershell
python -c "import cv2; import torch; import ultralytics; print('✅ All packages imported successfully!')"
```

### Test 2: Check OpenCV with Webcam
```powershell
python src/utils/video_handler.py
```

This will:
- Open your webcam
- Display the video feed
- Show frame information
- Press 'q' to quit

**Troubleshooting**:
- If webcam doesn't open, check if another application is using it
- On Windows, you may need to grant webcam permissions

---

## 📁 Step 4: Verify Project Structure

Run this to check all directories are created:

```powershell
python src/config.py
```

You should see:
```
✓ Directory ready: data/input_videos
✓ Directory ready: data/sample_videos
✓ Directory ready: outputs/processed_videos
✓ Directory ready: outputs/heatmaps
✓ Directory ready: outputs/reports
✓ Directory ready: models
```

---

## 🎥 Step 5: Get Sample Videos (Optional)

For testing, you can use:

1. **Your webcam** (easiest)
2. **Download sample retail videos**:
   - [Pexels - Free Stock Videos](https://www.pexels.com/search/videos/retail%20store/)
   - [Pixabay - Free Videos](https://pixabay.com/videos/search/shopping/)
   
3. **Place videos in**: `data/input_videos/`

---

## 🤖 Step 6: Download YOLO Model

The first time you run detection, YOLOv8 will auto-download.

To pre-download:
```powershell
python -c "from ultralytics import YOLO; model = YOLO('yolov8n.pt'); print('✅ YOLO model downloaded')"
```

Model will be saved in your home directory under `.cache/ultralytics/`

---

## ✅ Verification Checklist

- [ ] Virtual environment created and activated
- [ ] All packages installed without errors
- [ ] Webcam test runs successfully
- [ ] Project directories created
- [ ] Config file runs without errors
- [ ] YOLO model downloaded

---

## 🎓 What We've Set Up

1. **Project Structure**: Organized folders for code, data, and outputs
2. **Configuration System**: Centralized settings in `config.py`
3. **Video Handler**: Module to read/write videos and webcam
4. **Development Environment**: Isolated Python environment with all dependencies

---

## 🚀 Next Steps

Once setup is complete:
1. **Phase 1 Complete**: You now have the foundation
2. **Phase 2 Next**: Person detection with YOLO
3. **Test your video handler**: Run the webcam test

---

## 🐛 Common Issues

### Issue 1: "Python not recognized"
- Add Python to PATH
- Reinstall Python with "Add to PATH" checked

### Issue 2: "pip install fails"
- Update pip: `python -m pip install --upgrade pip`
- Try with: `pip install --no-cache-dir -r requirements.txt`

### Issue 3: "Webcam not working"
- Check if camera is in use by another app
- Try changing `WEBCAM_INDEX` in `config.py` from 0 to 1

### Issue 4: "torch/CUDA errors"
- For CPU-only: This is fine, will be slower
- For GPU: Install CUDA toolkit from NVIDIA

---

## 💡 Tips

- Keep virtual environment activated while working
- Run tests after making changes
- Check `config.py` to customize settings
- Read code comments - they explain concepts!

---

**Ready to build?** Let's start with Phase 2: Person Detection! 🚀
