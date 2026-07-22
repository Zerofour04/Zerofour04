#!/usr/bin/env python3
"""
Prepare a photo for ASCII conversion:
1. Remove background with rembg
2. Boost local contrast with CLAHE
3. Composite onto white background
"""

import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image
from rembg import remove


def prep_photo(input_path: str, output_path: str = "source-prepped.png"):
    # Load image
    img = Image.open(input_path).convert("RGBA")

    # Remove background
    img_no_bg = remove(img)

    # Convert to numpy for OpenCV processing
    img_array = np.array(img_no_bg)

    # Extract RGB and alpha
    rgb = img_array[:, :, :3]
    alpha = img_array[:, :, 3]

    # Convert to grayscale for CLAHE
    gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)

    # Apply CLAHE (Contrast Limited Adaptive Histogram Equalization)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)

    # Create white background
    result = np.full_like(enhanced, 255)

    # Composite: where alpha > 0, use the enhanced grayscale
    mask = alpha > 128
    result[mask] = enhanced[mask]

    # Save
    output = Image.fromarray(result, mode="L")
    output.save(output_path)
    print(f"Saved prepped photo to {output_path}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python prep_photo.py <input_image> [output_path]")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else "source-prepped.png"
    prep_photo(input_file, output_file)
