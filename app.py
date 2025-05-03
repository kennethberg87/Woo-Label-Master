import os
import logging
from flask import Flask, render_template, request, jsonify, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix
from apscheduler.schedulers.background import BackgroundScheduler
import atexit

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
# create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# configure the database, relative to the app instance folder
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
# initialize the app with the extension
db.init_app(app)

# Import after db is defined to avoid circular imports
from models import Settings, OrderHistory
from woocommerce_service import poll_woocommerce_orders
from printer_service import test_printer_connection

# Create scheduler
scheduler = BackgroundScheduler()

def initialize_scheduler():
    """Initialize the order polling scheduler based on current settings"""
    with app.app_context():
        # Get current settings
        settings = Settings.query.first()
        if not settings:
            logger.warning("No settings found, scheduler not started")
            return
        
        # Remove existing jobs
        for job in scheduler.get_jobs():
            scheduler.remove_job(job.id)
        
        # Add new job with current poll interval
        scheduler.add_job(
            func=poll_woocommerce_orders,
            trigger='interval',
            seconds=settings.poll_interval,
            id='poll_orders',
            args=[app]
        )
        
        logger.info(f"Scheduler initialized with interval of {settings.poll_interval} seconds")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/settings', methods=['GET', 'POST'])
def settings():
    if request.method == 'POST':
        # Save settings
        try:
            settings = Settings.query.first()
            if not settings:
                settings = Settings()
                db.session.add(settings)
            
            # WooCommerce settings
            settings.woocommerce_url = request.form.get('woocommerce_url')
            settings.woocommerce_consumer_key = request.form.get('woocommerce_consumer_key')
            settings.woocommerce_consumer_secret = request.form.get('woocommerce_consumer_secret')
            
            # Printer settings
            settings.printer_ip = request.form.get('printer_ip')
            settings.printer_port = int(request.form.get('printer_port') or 9100)
            settings.label_width = request.form.get('label_width')
            settings.label_height = request.form.get('label_height')
            
            # Other settings
            settings.image_directory = request.form.get('image_directory')
            settings.poll_interval = int(request.form.get('poll_interval') or 60)
            
            db.session.commit()
            flash('Settings saved successfully!', 'success')
            
            # Reinitialize scheduler with new settings
            initialize_scheduler()
            
            return redirect(url_for('settings'))
        except Exception as e:
            logger.error(f"Error saving settings: {e}")
            flash(f'Error saving settings: {str(e)}', 'danger')
            db.session.rollback()
    
    # Get current settings
    settings = Settings.query.first()
    return render_template('settings.html', settings=settings)

@app.route('/dashboard')
def dashboard():
    # Fetch recent order history
    recent_orders = OrderHistory.query.order_by(OrderHistory.timestamp.desc()).limit(50).all()
    return render_template('dashboard.html', orders=recent_orders)

@app.route('/api/test-printer', methods=['POST'])
def test_printer():
    data = request.json
    ip = data.get('ip')
    port = int(data.get('port', 9100))
    
    success, message = test_printer_connection(ip, port)
    return jsonify({'success': success, 'message': message})

@app.route('/api/test-woocommerce', methods=['POST'])
def test_woocommerce():
    from woocommerce_service import test_woocommerce_connection
    
    data = request.json
    url = data.get('url')
    consumer_key = data.get('consumer_key')
    consumer_secret = data.get('consumer_secret')
    
    success, message = test_woocommerce_connection(url, consumer_key, consumer_secret)
    return jsonify({'success': success, 'message': message})

@app.route('/api/test-print-label', methods=['POST'])
def test_print_label():
    """Test print a label to verify printer functionality"""
    from printer_service import print_label
    import os
    
    test_label_path = os.path.join(os.getcwd(), 'labels', 'TEST-LABEL.bmp')
    
    # Check if the test label exists
    if not os.path.isfile(test_label_path):
        # Try to create it if it doesn't exist
        try:
            from create_test_label import create_test_label
            test_label_path = create_test_label()
        except Exception as e:
            logger.error(f"Error creating test label: {e}")
            return jsonify({
                'success': False, 
                'message': f"Test label not found and couldn't be created: {str(e)}"
            })
    
    # Try to print the test label
    success, message = print_label(test_label_path)
    
    # Record the test print in the order history
    try:
        history = OrderHistory(
            order_id=0,
            sku="TEST-LABEL",
            product_name="Test Print Label",
            printed=success,
            error_message=None if success else message
        )
        db.session.add(history)
        db.session.commit()
    except Exception as e:
        logger.error(f"Error recording test print: {e}")
        # Don't return error here, as the print might have succeeded
    
    return jsonify({'success': success, 'message': message})

with app.app_context():
    # Make sure to import the models here or their tables won't be created
    import models  # noqa: F401
    
    db.create_all()
    
    # Initialize the scheduler after app context is available
    try:
        initialize_scheduler()
        scheduler.start()
        logger.info("Scheduler started")
        # Shut down the scheduler when exiting the app
        atexit.register(lambda: scheduler.shutdown())
    except Exception as e:
        logger.error(f"Error starting scheduler: {e}")
