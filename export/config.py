import os

class Config:
    """Base configuration class for the application."""
    # Flask configuration
    SECRET_KEY = os.environ.get('SESSION_SECRET', 'dev-secret-key')
    DEBUG = True
    
    # Database configuration
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_recycle': 300,
        'pool_pre_ping': True,
    }
    
    # Default printer settings
    DEFAULT_PRINTER_PORT = 9100
    DEFAULT_LABEL_WIDTH = 62  # in mm
    DEFAULT_POLL_INTERVAL = 60  # in seconds
