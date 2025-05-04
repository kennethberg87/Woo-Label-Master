import os
import socket
import logging
from PIL import Image
from brother_ql.raster import BrotherQLRaster
from brother_ql.brother_ql_create import create_label
# Instead of using the built-in send function, we'll implement our own
# from brother_ql.backends.helpers import send
from models import Settings

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def send_to_printer(printer_data, printer_ip, printer_port=9100):
    """
    Send data directly to a networked printer via TCP/IP.
    This function replaces the brother_ql.backends.helpers.send function
    which doesn't implement TCP/IP socket printing.
    """
    logger.debug(f"Attempting to send {len(printer_data)} bytes to {printer_ip}:{printer_port}")
    try:
        # Create a TCP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)  # 10-second timeout
        
        # Connect to the printer
        sock.connect((printer_ip, printer_port))
        
        # Send the data
        sock.sendall(printer_data)
        
        # Close the connection
        sock.close()
        
        logger.debug("Data sent successfully to printer")
        return {"status": True, "message": "Data sent successfully to printer"}
    except socket.timeout:
        logger.error(f"Connection to {printer_ip}:{printer_port} timed out")
        return {"status": False, "error": "Connection to printer timed out"}
    except socket.error as e:
        logger.error(f"Socket error while sending data to printer: {e}")
        return {"status": False, "error": f"Socket error: {str(e)}"}
    except Exception as e:
        logger.error(f"Error sending data to printer: {e}")
        return {"status": False, "error": str(e)}

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
            # Use our custom send_to_printer function instead of the standard send function
            status = send_to_printer(instructions, printer_ip, printer_port)
            
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
