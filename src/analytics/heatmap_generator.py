"""
Heatmap Generator Module

Generates visual heatmaps showing crowd density and popular areas in the store.
Creates color-coded overlays (RED=high traffic, GREEN/BLUE=low traffic).

Key Features:
- Accumulates person positions over entire video
- Generates density heatmap
- Creates color-coded overlay (hot/medium/cold zones)
- Blends with video frames for visualization

Author: Smart Retail Analytics Team
Phase: 5 - Advanced Analytics
"""

import numpy as np
import cv2
from pathlib import Path
import sys

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))
from config import *


class HeatmapGenerator:
    """
    Generates heatmaps showing where people spend most time in the store.
    
    Accumulates position data throughout video processing and creates
    a visual density map with color coding:
    - RED: High traffic areas (hot spots)
    - YELLOW/ORANGE: Medium traffic
    - GREEN/BLUE: Low traffic (cold spots)
    
    Attributes:
        heatmap: Accumulated density map
        frame_width: Width of video frame
        frame_height: Height of video frame
        blur_kernel: Gaussian blur size for smoothing
    """
    
    def __init__(self, frame_width, frame_height, blur_kernel=(25, 25)):
        """
        Initialize the Heatmap Generator.
        
        Args:
            frame_width: Width of video frame
            frame_height: Height of video frame
            blur_kernel: Kernel size for Gaussian blur (must be odd)
        """
        self.frame_width = frame_width
        self.frame_height = frame_height
        self.blur_kernel = blur_kernel
        
        # Initialize empty heatmap
        self.heatmap = np.zeros((frame_height, frame_width), dtype=np.float32)
        self.accumulation_count = 0
        
        # Heatmap parameters
        self.radius = 30  # Radius of influence for each person
        self.intensity = 1.0  # Intensity value to add
        
        print(f"✅ Heatmap Generator initialized ({frame_width}x{frame_height})")
    
    def add_positions(self, tracked_objects):
        """
        Add person positions to the heatmap.
        
        Args:
            tracked_objects: List of tracked objects with 'center' key
        """
        for obj in tracked_objects:
            cx, cy = obj['center']
            
            # Add Gaussian-like blob at person's position
            # Using cv2.circle with thickness=-1 for filled circle
            cv2.circle(self.heatmap, (int(cx), int(cy)), 
                      self.radius, self.intensity, -1)
        
        self.accumulation_count += 1
    
    def generate_heatmap_overlay(self, frame, alpha=0.5):
        """
        Generate color-coded heatmap overlay blended with original frame.
        
        Args:
            frame: Original video frame
            alpha: Transparency (0.0=transparent, 1.0=opaque heatmap)
        
        Returns:
            frame: Frame with heatmap overlay
        """
        if self.accumulation_count == 0:
            return frame
        
        # Apply Gaussian blur for smooth heatmap
        blurred = cv2.GaussianBlur(self.heatmap, self.blur_kernel, 0)
        
        # Normalize to 0-255 range
        normalized = cv2.normalize(blurred, None, 0, 255, cv2.NORM_MINMAX)
        heatmap_8bit = normalized.astype(np.uint8)
        
        # Apply colormap (COLORMAP_JET: blue=cold, red=hot)
        colored_heatmap = cv2.applyColorMap(heatmap_8bit, cv2.COLORMAP_JET)
        
        # Create mask to only show areas with activity
        _, mask = cv2.threshold(heatmap_8bit, 10, 255, cv2.THRESH_BINARY)
        mask_3channel = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)
        
        # Apply mask to colored heatmap
        masked_heatmap = cv2.bitwise_and(colored_heatmap, mask_3channel)
        
        # Blend with original frame
        overlay = cv2.addWeighted(frame, 1.0 - alpha, masked_heatmap, alpha, 0)
        
        return overlay
    
    def save_heatmap(self, output_path):
        """
        Save standalone heatmap as image file.
        
        Args:
            output_path: Path to save heatmap image
        """
        if self.accumulation_count == 0:
            print("⚠️  No heatmap data to save")
            return
        
        # Generate colored heatmap
        blurred = cv2.GaussianBlur(self.heatmap, self.blur_kernel, 0)
        normalized = cv2.normalize(blurred, None, 0, 255, cv2.NORM_MINMAX)
        heatmap_8bit = normalized.astype(np.uint8)
        colored_heatmap = cv2.applyColorMap(heatmap_8bit, cv2.COLORMAP_JET)
        
        # Add legend/info
        legend_height = 80
        canvas = np.zeros((self.frame_height + legend_height, 
                          self.frame_width, 3), dtype=np.uint8)
        
        # Place heatmap
        canvas[0:self.frame_height, 0:self.frame_width] = colored_heatmap
        
        # Add legend
        legend_y = self.frame_height + 20
        cv2.putText(canvas, "HEATMAP LEGEND:", (10, legend_y),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        # Color gradient legend
        legend_y += 30
        gradient_width = 300
        gradient = np.linspace(0, 255, gradient_width).astype(np.uint8)
        gradient = np.repeat(gradient[np.newaxis, :], 20, axis=0)
        gradient_colored = cv2.applyColorMap(gradient, cv2.COLORMAP_JET)
        
        canvas[legend_y:legend_y+20, 10:10+gradient_width] = gradient_colored
        
        # Labels
        cv2.putText(canvas, "Low", (10, legend_y + 35),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        cv2.putText(canvas, "Medium", (140, legend_y + 35),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        cv2.putText(canvas, "High", (280, legend_y + 35),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        # Save
        cv2.imwrite(str(output_path), canvas)
        print(f"🔥 Heatmap saved: {output_path}")
    
    def get_hotspots(self, threshold=0.7, min_area=500):
        """
        Identify hotspot regions (high traffic areas).
        
        Args:
            threshold: Threshold for considering area as hotspot (0.0-1.0)
            min_area: Minimum area in pixels to be considered a hotspot
        
        Returns:
            list: List of hotspot contours
        """
        if self.accumulation_count == 0:
            return []
        
        # Generate normalized heatmap
        blurred = cv2.GaussianBlur(self.heatmap, self.blur_kernel, 0)
        normalized = cv2.normalize(blurred, None, 0, 1, cv2.NORM_MINMAX)
        
        # Threshold to find hotspots
        _, binary = cv2.threshold(normalized, threshold, 1, cv2.THRESH_BINARY)
        binary_8bit = (binary * 255).astype(np.uint8)
        
        # Find contours
        contours, _ = cv2.findContours(binary_8bit, cv2.RETR_EXTERNAL, 
                                       cv2.CHAIN_APPROX_SIMPLE)
        
        # Filter by area
        hotspots = [c for c in contours if cv2.contourArea(c) >= min_area]
        
        return hotspots
    
    def draw_hotspot_labels(self, frame, threshold=0.7, min_area=500):
        """
        Draw labels on identified hotspots.
        
        Args:
            frame: Video frame to draw on
            threshold: Hotspot detection threshold
            min_area: Minimum hotspot area
        
        Returns:
            frame: Frame with hotspot labels
        """
        hotspots = self.get_hotspots(threshold, min_area)
        
        for idx, contour in enumerate(hotspots, 1):
            # Get centroid
            M = cv2.moments(contour)
            if M['m00'] != 0:
                cx = int(M['m10'] / M['m00'])
                cy = int(M['m01'] / M['m00'])
                
                # Draw contour
                cv2.drawContours(frame, [contour], -1, (0, 0, 255), 2)
                
                # Draw label
                label = f"HOT SPOT {idx}"
                cv2.putText(frame, label, (cx - 50, cy),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
        
        return frame
    
    def get_statistics(self):
        """
        Get heatmap statistics.
        
        Returns:
            dict: Statistics including max density, hotspot count, etc.
        """
        hotspots = self.get_hotspots()
        
        return {
            'accumulation_frames': self.accumulation_count,
            'max_density': float(np.max(self.heatmap)),
            'mean_density': float(np.mean(self.heatmap[self.heatmap > 0])) if np.any(self.heatmap > 0) else 0,
            'hotspot_count': len(hotspots),
            'coverage_percentage': float(np.count_nonzero(self.heatmap) / self.heatmap.size * 100)
        }
    
    def print_summary(self):
        """Print heatmap statistics summary."""
        stats = self.get_statistics()
        
        print("\n" + "="*60)
        print("HEATMAP ANALYSIS SUMMARY")
        print("="*60)
        print(f"🔥 Frames Accumulated:    {stats['accumulation_frames']}")
        print(f"🔥 Hotspots Identified:   {stats['hotspot_count']}")
        print(f"🔥 Max Density:           {stats['max_density']:.2f}")
        print(f"🔥 Mean Density:          {stats['mean_density']:.2f}")
        print(f"🔥 Coverage:              {stats['coverage_percentage']:.1f}%")
        print("="*60)
