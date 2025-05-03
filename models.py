from datetime import datetime
from app import db

class Settings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    
    # WooCommerce API settings
    woocommerce_url = db.Column(db.String(255))
    woocommerce_consumer_key = db.Column(db.String(255))
    woocommerce_consumer_secret = db.Column(db.String(255))
    
    # Printer settings
    printer_ip = db.Column(db.String(50))
    printer_port = db.Column(db.Integer, default=9100)
    label_width = db.Column(db.String(20), default="62")  # in mm
    label_height = db.Column(db.String(20), default="AUTO")  # AUTO or specific height in mm
    
    # Directory settings
    image_directory = db.Column(db.String(255))
    
    # Application settings
    poll_interval = db.Column(db.Integer, default=60)  # in seconds
    
    def __repr__(self):
        return f"<Settings {self.id}>"

class OrderHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer)
    sku = db.Column(db.String(100))
    product_name = db.Column(db.String(255))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    printed = db.Column(db.Boolean, default=False)
    error_message = db.Column(db.Text, nullable=True)
    
    def __repr__(self):
        return f"<OrderHistory {self.order_id} - {self.sku}>"
