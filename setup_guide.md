# WooCommerce Label Printer - Local Installation Guide

This guide will help you install the WooCommerce Label Printer application on your Ubuntu server.

## Step 1: Download and Extract the Application

1. Download the `woo-label-printer.tar.gz` file
2. Create a directory for the application
   ```bash
   mkdir -p /opt/woo-label-printer
   ```
3. Extract the application files
   ```bash
   tar -xzvf woo-label-printer.tar.gz -C /opt/woo-label-printer
   cd /opt/woo-label-printer
   ```

## Step 2: Set Up Python Environment

1. Make sure Python 3.9+ is installed
   ```bash
   python3 --version
   # Should be 3.9.0 or higher
   ```

2. Install system dependencies
   ```bash
   sudo apt update
   sudo apt install -y python3-venv python3-pip postgresql libpq-dev
   ```

3. Create and activate a virtual environment
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

4. Install required Python packages
   ```bash
   pip install -r requirements.txt
   ```

## Step 3: Set Up PostgreSQL Database

1. Create a database and user
   ```bash
   sudo -u postgres psql
   ```

2. In the PostgreSQL prompt, run:
   ```sql
   CREATE DATABASE woollprinter;
   CREATE USER woollprinteruser WITH ENCRYPTED PASSWORD 'your_secure_password';
   GRANT ALL PRIVILEGES ON DATABASE woollprinter TO woollprinteruser;
   \q
   ```

3. Set the database URL environment variable
   ```bash
   export DATABASE_URL="postgresql://woollprinteruser:your_secure_password@localhost/woollprinter"
   ```

4. Create an environment file for persistence
   ```bash
   echo "DATABASE_URL=postgresql://woollprinteruser:your_secure_password@localhost/woollprinter" > .env
   echo "SESSION_SECRET=your_secure_random_string" >> .env
   ```

## Step 4: Start the Application

1. Run the application using Gunicorn
   ```bash
   gunicorn --bind 0.0.0.0:5000 --workers=2 main:app
   ```

2. Access the web interface at `http://your-server-ip:5000`

## Step 5: Configure the Application

1. Go to the Settings page
2. Enter your WooCommerce API credentials:
   - Store URL
   - Consumer Key
   - Consumer Secret
3. Configure your printer settings:
   - IP address
   - Port (default: 9100)
   - Label width (62mm for the Brother QL-720NW)
4. Set the labels directory path:
   - Default: `/opt/woo-label-printer/labels`
5. Set the polling interval (in seconds)
6. Save your settings

## Step 6: Set Up as a System Service (For Automatic Startup)

1. Create a systemd service file
   ```bash
   sudo nano /etc/systemd/system/woo-label-printer.service
   ```

2. Add the following content (replace paths and username with your own):
   ```
   [Unit]
   Description=WooCommerce Label Printer Service
   After=network.target postgresql.service
   
   [Service]
   User=your_username
   Group=your_username
   WorkingDirectory=/opt/woo-label-printer
   Environment="PATH=/opt/woo-label-printer/venv/bin"
   EnvironmentFile=/opt/woo-label-printer/.env
   ExecStart=/opt/woo-label-printer/venv/bin/gunicorn --workers=2 --bind 0.0.0.0:5000 main:app
   Restart=always
   
   [Install]
   WantedBy=multi-user.target
   ```

3. Enable and start the service
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable woo-label-printer.service
   sudo systemctl start woo-label-printer.service
   ```

4. Check the service status
   ```bash
   sudo systemctl status woo-label-printer.service
   ```

## Step 7: Adding Your Own Label Files

1. Place your BMP format label images in the `labels` directory
2. Name each file with the exact SKU of the product (e.g., "ABC123.bmp")
3. Images should be sized to fit your label width (62mm = approximately 696 pixels at 300 DPI)

## Step 8: Testing the Setup

1. On the Settings page, use the "Test Printer Connection" button to verify the printer connection
2. Use the "Print Test Label" button to print a sample label
3. Use the "Test WooCommerce Connection" button to verify API access

## Troubleshooting

- Check logs for errors: `sudo journalctl -u woo-label-printer.service`
- Verify network connectivity to both WooCommerce store and printer
- Ensure your label images are correctly named and formatted
- Check database connection and environment variables