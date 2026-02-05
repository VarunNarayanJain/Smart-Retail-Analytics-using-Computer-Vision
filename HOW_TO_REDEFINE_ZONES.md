# 🔄 How to Redefine Store Zones and Sections

## Problem: "I want to redefine my sections!"

When you run `--analytics` the second time, it loads your previously saved zones and sections. Here's how to redefine them.

---

## ✅ Solution 1: Interactive Prompts (EASIEST!)

Just run the command normally:
```powershell
python main.py --video "data/input_videos/retail.mp4" --analytics
```

**The system will ask you:**

### **Step 1: Store Boundary Prompt**
```
✅ Loaded saved store zone
============================================================
Do you want to REDEFINE store boundary? (yes/no):
```

**Type your answer:**
- `yes` or `y` → Opens selection UI to redraw store boundary
- `no` or `n` → Uses saved store boundary (skips to sections)

---

### **Step 2: Sections Prompt**
```
✅ Loaded 1 saved sections:
   1. electronics
============================================================
Do you want to REDEFINE sections? (yes/no):
```

**Type your answer:**
- `yes` or `y` → Opens selection UI to define NEW sections (replaces old ones)
- `no` or `n` → Uses saved sections (goes to processing)

---

### **If You Answer "yes" to Sections:**

You'll be able to define as many sections as you want:

```
Enter name for Section 1 (or 'q' to finish): Electronics
[Window opens - click points to define Electronics boundary]

Enter name for Section 2 (or 'q' to finish): Clothing
[Window opens - click points to define Clothing boundary]

Enter name for Section 3 (or 'q' to finish): Groceries
[Window opens - click points to define Groceries boundary]

Enter name for Section 4 (or 'q' to finish): Checkout
[Window opens - click points to define Checkout boundary]

Enter name for Section 5 (or 'q' to finish): q
[Done! Processing starts]
```

**Result:** Your new sections replace the old ones!

---

## ✅ Solution 2: Use Command-Line Flag (NO PROMPTS)

If you don't want interactive prompts, use the flag:

```powershell
python main.py --video "data/input_videos/retail.mp4" --analytics --redefine-zones
```

**What happens:**
- ✅ Skips all prompts
- ✅ Forces reselection of BOTH store zone AND sections
- ✅ Goes straight to selection UI

---

## ✅ Solution 3: Delete Saved Files (MANUAL)

Delete the saved configuration files:

```powershell
# Delete store zone
Remove-Item zones\retail_zone.json

# Delete sections
Remove-Item sections\retail_sections.json

# Run analytics
python main.py --video "data/input_videos/retail.mp4" --analytics
```

**Result:** System treats it as first-time run, asks you to define everything.

---

## 📋 Comparison of Methods

| Method | Store Zone | Sections | Prompts | Best For |
|--------|------------|----------|---------|----------|
| **Interactive Prompts** | Choose to keep or redefine | Choose to keep or redefine | Yes | Most flexible! |
| **--redefine-zones Flag** | Always redefines | Always redefines | No | Quick full reset |
| **Delete Files** | Redefines (file missing) | Redefines (file missing) | No | Clean slate |

---

## 🎯 Your Scenario Solution

Based on your situation (you have 1 section called "electronics" but want to define more):

### **Recommended: Use Interactive Prompt**

```powershell
python main.py --video "data/input_videos/retail.mp4" --analytics
```

**When prompted:**
```
Do you want to REDEFINE store boundary? (yes/no): no
[Keeps your existing store zone]

Do you want to REDEFINE sections? (yes/no): yes
[Lets you define NEW sections]
```

**Then define multiple sections:**
```
Enter name for Section 1 (or 'q' to finish): Electronics
[Define Electronics area]

Enter name for Section 2 (or 'q' to finish): Clothing  
[Define Clothing area]

Enter name for Section 3 (or 'q' to finish): Groceries
[Define Groceries area]

Enter name for Section 4 (or 'q' to finish): Checkout
[Define Checkout area]

Enter name for Section 5 (or 'q' to finish): q
[Processing starts with 4 sections!]
```

✅ **Your new sections (Electronics, Clothing, Groceries, Checkout) will REPLACE the old one (electronics)!**

---

## 💡 Pro Tips

### **Tip 1: Keep Store Zone, Redefine Sections**
If your store boundary is correct but you want different sections:
- Answer `no` to store boundary prompt
- Answer `yes` to sections prompt
- ✅ Saves time!

### **Tip 2: Section Names Matter**
Use clear, consistent names:
- ✅ Good: "Electronics", "Clothing", "Groceries"
- ❌ Bad: "elec", "electronics dept", "Electronics Area"

### **Tip 3: How Many Sections?**
Recommended: **3-6 sections** for best results
- Too few (1-2): Not enough detail
- Too many (10+): Cluttered display, hard to manage

### **Tip 4: Section Boundaries**
- Don't overlap sections (people will be counted in both)
- Cover the main walkable areas
- Don't include walls/corners

---

## 🔍 Check What's Currently Saved

Want to see what zones/sections are currently saved?

### **Check Store Zone:**
```powershell
Get-Content zones\retail_zone.json
```

### **Check Sections:**
```powershell
Get-Content sections\retail_sections.json
```

Example output:
```json
{
  "video": "data\\input_videos\\retail.mp4",
  "sections": [
    {
      "name": "electronics",
      "points": [[8, 51], [193, 40], [245, 330], [22, 356]]
    }
  ]
}
```

This shows you currently have **1 section called "electronics"**.

---

## 🎬 Complete Walkthrough

**Your situation:** 1 saved section ("electronics"), want to define more.

### **Step-by-Step:**

1. **Run command:**
   ```powershell
   python main.py --video "data/input_videos/retail.mp4" --analytics
   ```

2. **Store boundary prompt appears:**
   ```
   Do you want to REDEFINE store boundary? (yes/no): 
   ```
   Type: `no` (Enter)

3. **Sections prompt appears:**
   ```
   ✅ Loaded 1 saved sections:
      1. electronics
   Do you want to REDEFINE sections? (yes/no):
   ```
   Type: `yes` (Enter)

4. **Define sections one by one:**
   ```
   Enter name for Section 1 (or 'q' to finish): 
   ```
   
   **Your sections (example for retail store):**
   - Section 1: `Electronics`
   - Section 2: `Clothing`
   - Section 3: `Groceries`
   - Section 4: `Checkout`
   - Type `q` when done

5. **For each section:**
   - Window opens with first video frame
   - Left-click to add boundary points (4-8 points)
   - Right-click when done
   - Window closes, next section prompt appears

6. **Processing starts:**
   ```
   ✅ Total sections defined: 4
   🔄 Initializing analytics modules...
   🎬 Processing video...
   ```

7. **View results:**
   - Video: `analytics_retail.mp4` (with all 4 sections shown!)
   - Heatmap: `heatmap_retail.jpg`
   - Logs: `section_analysis.csv` (data for all 4 sections)

---

## ✅ Success!

After following these steps, you'll have:
- ✅ Your original store boundary (kept from before)
- ✅ 4 new sections (Electronics, Clothing, Groceries, Checkout)
- ✅ Complete analytics video showing all sections
- ✅ Section-wise occupancy data

**Next time you run the command, it will load your 4 sections automatically!**

---

## 🆘 Still Having Issues?

### **Issue: Prompt doesn't appear**
**Solution:** You might be using `--redefine-zones` flag. Remove it:
```powershell
# Wrong (skips prompts):
python main.py --video retail.mp4 --analytics --redefine-zones

# Correct (shows prompts):
python main.py --video retail.mp4 --analytics
```

### **Issue: Can't type in console**
**Solution:** Make sure the OpenCV window is not in focus. Click on the PowerShell/terminal window first.

### **Issue: Section window won't close**
**Solution:** After clicking points, **right-click** to complete the section. Don't just close the window.

---

**That's it! You now know 3 ways to redefine zones and sections! 🎉**
