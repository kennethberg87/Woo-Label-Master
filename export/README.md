# WooCommerce Label Printer

A Python Flask application that automatically monitors your WooCommerce store for new orders and prints matching product labels on a Brother QL-720NW label printer.

## Features

- Web interface for configuration and monitoring
- Automatic polling of WooCommerce orders via API
- Direct printing to Brother QL-720NW network printers
- Label printing based on product SKUs
- Order history tracking with print status
- Dashboard with print statistics

## Requirements

- Python 3.9+
- PostgreSQL database
- Brother QL-720NW label printer (connected via network)
- WooCommerce store with API access

## Installation Guide

### 1. Set up Environment

```bash
# Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate
```

### 2. Install Dependencies

```bash
# Install required packages
pip install apscheduler brother-ql email-validator flask flask-sqlalchemy gunicorn pillow psycopg2-binary woocommerce
```

### 3. Set up Database

```bash
# Create a PostgreSQL database
# Example PostgreSQL setup:
createdb woollprinter
```

### 4. Configure Environment

Create a file named `.env` in the application directory:

```
DATABASE_URL=postgresql://username:password@localhost/woollprinter
SESSION_SECRET=your_secure_random_string
```

### 5. Start the Application

```bash
# Run the application
gunicorn --bind 0.0.0.0:5000 main:app
```

### 6. Configuration

1. Access the web interface at http://localhost:5000
2. Navigate to the Settings page and configure:
   - WooCommerce API credentials (URL, consumer key, consumer secret)
   - Printer settings (IP address, port, label size)
   - Labels directory path
   - Polling interval

## Usage

1. Create label images for your products:
   - BMP format
   - Named with the product SKU (e.g., "ABC123.bmp")
   - Sized for your label dimensions (default 62mm width)

2. Place the label images in your configured labels directory

3. When orders are placed on your WooCommerce store with matching SKUs, the application will automatically print the corresponding labels.

## Testing

- Use the Test Printer Connection button to verify printer connectivity
- Use the Print Test Label button to print a sample 62mm label
- Use the Test WooCommerce Connection button to verify API access

## Systemd Service Setup (For Ubuntu/Debian)

Create file `/etc/systemd/system/woo-label-printer.service`:

```
[Unit]
Description=WooCommerce Label Printer Service
After=network.target postgresql.service

[Service]
User=your_username
Group=your_username
WorkingDirectory=/path/to/application
Environment="PATH=/path/to/application/venv/bin"
EnvironmentFile=/path/to/application/.env
ExecStart=/path/to/application/venv/bin/gunicorn --workers=2 --bind 0.0.0.0:5000 main:app
Restart=always

[Install]
WantedBy=multi-user.target
```

Then enable and start the service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable woo-label-printer.service
sudo systemctl start woo-label-printer.service
```

## Troubleshooting

- Check the application logs for error messages
- Verify network connectivity to both WooCommerce and the printer
- Ensure label images exist in the configured directory and match SKUs exactly