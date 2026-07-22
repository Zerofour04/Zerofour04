#!/usr/bin/env python3
"""
Prep photo without rembg - uses threshold for light backgrounds.
Works well for portraits with uniform light gray/white backgrounds.
"""

import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image


def prep_photo(input_path: str, output_path: str = "source-prepped.png"):
    # Load image
    img = cv2.imread(input_path)
    if img is None:
        print(f"Error: Could not load {input_path}")
        return

    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Apply CLAHE for better contrast (the key step!)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)

    # Threshold to find the light background (> 200 is background)
    _, mask = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)

    # Invert mask (subject = white, background = black)
    mask_inv = cv2.bitwise_not(mask)

    # Dilate mask slightly to avoid edge artifacts
    kernel = np.ones((3, 3), np.uint8)
    mask_inv = cv2.dilate(mask_inv, kernel, iterations=1)

    # Create white background
    result = np.full_like(enhanced, 255)

    # Composite: use enhanced image where mask is white (subject)
    result = np.where(mask_inv > 128, enhanced, 255)

    # Save
    cv2.imwrite(output_path, result)
    print(f"Saved prepped photo to {output_path}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        # Default to source-photo.png
        input_file = "source-photo.png"
    else:
        input_file = sys.argv[1]

    output_file = sys.argv[2] if len(sys.argv) > 2 else "source-prepped.png"
    prep_photo(input_file, output_file)
