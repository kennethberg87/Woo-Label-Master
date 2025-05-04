#!/usr/bin/env python3
from PIL import Image, ImageDraw, ImageFont
import os

def create_test_label(width=696, height=271, sku="TEST-LABEL"):
    """
    Create a test label image with the specified dimensions.
    Width of 696 pixels corresponds to 62mm at 300 DPI for Brother QL-720NW.
    """
    # Create a white background image
    image = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(image)
    
    # Try to use a default font, or fall back to default
    try:
        # Try to load a font
        font_large = ImageFont.truetype("Arial", 36)
        font_medium = ImageFont.truetype("Arial", 24)
        font_small = ImageFont.truetype("Arial", 16)
    except IOError:
        # If the font is not available, use default font
        font_large = ImageFont.load_default()
        font_medium = font_large
        font_small = font_large
    
    # Add a border
    draw.rectangle(((0, 0), (width-1, height-1)), outline='black', width=2)
    
    # Add text
    draw.text((width//2, 40), f"Test Label: {sku}", font=font_large, fill='black', anchor='mm')
    draw.text((width//2, 90), "Brother QL-720NW", font=font_medium, fill='black', anchor='mm')
    draw.text((width//2, 130), "62mm x 29mm", font=font_medium, fill='black', anchor='mm')
    
    # Add SKU barcode simulation
    draw.rectangle(((width//4, 170), (3*width//4, 210)), fill='white', outline='black')
    draw.text((width//2, 190), sku, font=font_small, fill='black', anchor='mm')
    
    # Add current date at the bottom
    draw.text((width//2, height-20), "WooCommerce Label Printer", font=font_small, fill='black', anchor='mm')
    
    # Save the image
    save_path = os.path.join('labels', f"{sku}.bmp")
    image.save(save_path)
    print(f"Test label created at: {save_path}")
    return save_path

if __name__ == "__main__":
    # Create a test label with 62mm width (696 pixels at 300 DPI)
    create_test_label()