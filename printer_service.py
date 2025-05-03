import os
import socket
import logging
from PIL import Image
from brother_ql.raster import BrotherQLRaster
from brother_ql.brother_ql_create import create_label
from brother_ql.backends.helpers import send
from models import Settings

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def get_printer_settings():
    """Get printer settings from the database"""
    from app import db
    from models import Settings
    
    settings = Settings.query.first()
    if not settings:
        logger.error("Printer settings not configured")
        return None
    
    if not settings.printer_ip:
        logger.error("Printer IP not configured")
        return None
    
    return settings

def test_printer_connection(ip, port):
    """Test the connection to the printer"""
    try:
        # Try to establish a socket connection to the printer
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)  # 5-second timeout
        
        # Attempt to connect to the printer
        result = sock.connect_ex((ip, port))
        sock.close()
        
        if result == 0:
            return True, "Successfully connected to printer"
        else:
            return False, f"Could not connect to printer at {ip}:{port}"
    except Exception as e:
        logger.error(f"Error testing printer connection: {e}")
        return False, f"Error connecting to printer: {str(e)}"

def print_label(image_path):
    """Print a label using the Brother QL printer"""
    settings = get_printer_settings()
    if not settings:
        return False, "Printer settings not configured"
    
    try:
        # Get printer settings
        printer_ip = settings.printer_ip
        printer_port = settings.printer_port
        label_width = settings.label_width
        label_height = "auto" if settings.label_height == "AUTO" else settings.label_height
        
        # Check if the image file exists
        if not os.path.isfile(image_path):
            return False, f"Image file not found: {image_path}"
        
        # Create a raster object
        qlr = BrotherQLRaster('QL-720NW')
        
        # Open the image file
        im = Image.open(image_path)
        
        # Determine label size format
        label_size = label_width
        if label_height != "auto":
            label_size = f"{label_width}x{label_height}"
        
        # Create the label
        create_label(qlr, im, label_size, threshold=70, cut=True)
        
        # Get the command instructions
        instructions = qlr.data
        
        # Send the print job to the printer
        try:
            status = send(instructions, printer_ip, printer_port)
            
            if status["status"]:
                logger.info(f"Successfully printed label: {image_path}")
                return True, "Label printed successfully"
            else:
                error_msg = status.get("error", "Unknown printer error")
                logger.error(f"Error printing label: {error_msg}")
                return False, f"Error printing label: {error_msg}"
        except Exception as e:
            logger.error(f"Error sending data to printer: {e}")
            return False, f"Error sending data to printer: {str(e)}"
            
    except Exception as e:
        logger.error(f"Error printing label: {e}")
        return False, f"Error printing label: {str(e)}"
