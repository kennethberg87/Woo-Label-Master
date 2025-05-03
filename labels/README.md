# Label Images Directory

This directory is where you should place your label image files for the WooCommerce Label Printer application.

## Important Notes:

1. **File Naming**: All label images should be named using the product SKU as the filename with a `.bmp` extension.
   - Example: If your product SKU is `ABC123`, the image file should be `ABC123.bmp`

2. **File Format**: Images must be in BMP format for compatibility with the Brother QL printer.

3. **Image Size**: Images should be properly sized to fit your label dimensions. The settings page allows you to specify the width and height of your labels.

4. **Path Configuration**: Make sure to set this directory path in the Settings page of the application.
   - The absolute path to this directory is: `/home/runner/workspace/labels`

## Example:
- Product SKU: `ABC123`
- Label Image File: `ABC123.bmp`
- Path Configuration in Settings: `/home/runner/workspace/labels`