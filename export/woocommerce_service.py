import os
import logging
import time
from woocommerce import API
from flask import current_app
from models import Settings, OrderHistory
from app import db
from printer_service import print_label

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def get_woocommerce_api():
    """Get the WooCommerce API instance from current settings"""
    settings = Settings.query.first()
    if not settings or not all([settings.woocommerce_url, 
                              settings.woocommerce_consumer_key, 
                              settings.woocommerce_consumer_secret]):
        logger.error("WooCommerce settings not configured")
        return None
    
    try:
        wcapi = API(
            url=settings.woocommerce_url,
            consumer_key=settings.woocommerce_consumer_key,
            consumer_secret=settings.woocommerce_consumer_secret,
            version="wc/v3"
        )
        return wcapi
    except Exception as e:
        logger.error(f"Error creating WooCommerce API: {e}")
        return None

def test_woocommerce_connection(url, consumer_key, consumer_secret):
    """Test WooCommerce API connection with the provided credentials"""
    try:
        wcapi = API(
            url=url,
            consumer_key=consumer_key,
            consumer_secret=consumer_secret,
            version="wc/v3"
        )
        response = wcapi.get("system_status")
        if response.status_code == 200:
            return True, "Successfully connected to WooCommerce API"
        else:
            return False, f"Error connecting to WooCommerce API: {response.status_code} - {response.reason}"
    except Exception as e:
        logger.error(f"Error testing WooCommerce connection: {e}")
        return False, f"Error connecting to WooCommerce API: {str(e)}"

def get_new_orders(wcapi, since_id=0):
    """Get new orders from WooCommerce API"""
    try:
        # Get orders that are after the specified order ID
        params = {
            'after': time.strftime('%Y-%m-%dT%H:%M:%S', time.gmtime(time.time() - 3600)),  # Last hour
            'per_page': 20,
            'status': 'processing,completed',  # Only get processing and completed orders
        }
        
        if since_id > 0:
            params['after_id'] = since_id
            
        response = wcapi.get("orders", params=params)
        
        if response.status_code != 200:
            logger.error(f"Error fetching orders: {response.status_code} - {response.reason}")
            return []
        
        return response.json()
    except Exception as e:
        logger.error(f"Error getting new orders: {e}")
        return []

def extract_skus_from_order(order):
    """Extract SKUs from a WooCommerce order"""
    skus = []
    
    if 'line_items' not in order:
        return skus
    
    for item in order['line_items']:
        sku = item.get('sku', '')
        if sku:
            skus.append({
                'sku': sku,
                'product_name': item.get('name', 'Unknown Product'),
                'quantity': item.get('quantity', 1)
            })
    
    return skus

def poll_woocommerce_orders(app):
    """Poll WooCommerce API for new orders and process them"""
    with app.app_context():
        logger.debug("Polling WooCommerce for new orders")
        
        settings = Settings.query.first()
        if not settings:
            logger.error("Settings not configured, skipping polling")
            return
        
        # Get the WooCommerce API
        wcapi = get_woocommerce_api()
        if not wcapi:
            return
        
        # Get the last processed order ID
        last_order = OrderHistory.query.order_by(OrderHistory.order_id.desc()).first()
        last_order_id = last_order.order_id if last_order else 0
        
        # Get new orders
        new_orders = get_new_orders(wcapi, last_order_id)
        logger.debug(f"Found {len(new_orders)} new orders")
        
        # Process each order
        for order in new_orders:
            order_id = order.get('id', 0)
            logger.debug(f"Processing order {order_id}")
            
            # Extract SKUs from the order
            sku_items = extract_skus_from_order(order)
            
            for sku_item in sku_items:
                sku = sku_item['sku']
                product_name = sku_item['product_name']
                
                # Check if the image file exists
                image_path = os.path.join(settings.image_directory, f"{sku}.bmp")
                if not os.path.isfile(image_path):
                    logger.debug(f"SKU image file not found: {image_path}")
                    
                    # Record in order history
                    history = OrderHistory(
                        order_id=order_id,
                        sku=sku,
                        product_name=product_name,
                        printed=False,
                        error_message=f"Image file not found: {sku}.bmp"
                    )
                    db.session.add(history)
                    continue
                
                # Try to print the label
                logger.debug(f"Printing label for SKU: {sku}")
                success, message = print_label(image_path)
                
                # Record in order history
                history = OrderHistory(
                    order_id=order_id,
                    sku=sku,
                    product_name=product_name,
                    printed=success,
                    error_message=None if success else message
                )
                db.session.add(history)
            
        # Commit all changes to the database
        db.session.commit()
