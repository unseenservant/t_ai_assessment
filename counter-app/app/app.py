import os
import time
import uuid
import logging
import sys
from flask import Flask, jsonify, request, render_template, g
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import OperationalError
from prometheus_flask_exporter import PrometheusMetrics
from pythonjsonlogger import jsonlogger

# Configure logging
class CustomJsonFormatter(jsonlogger.JsonFormatter):
    def add_fields(self, log_record, record, message_dict):
        super(CustomJsonFormatter, self).add_fields(log_record, record, message_dict)
        log_record['level'] = record.levelname
        log_record['logger'] = record.name
        # Add request_id if available
        if hasattr(g, 'request_id'):
            log_record['request_id'] = g.request_id

# Setup logger
logger = logging.getLogger()
logHandler = logging.StreamHandler(sys.stdout)
formatter = CustomJsonFormatter('%(timestamp)s %(level)s %(name)s %(message)s')
logHandler.setFormatter(formatter)
logger.addHandler(logHandler)
logger.setLevel(logging.INFO)

# Create Flask app
app = Flask(__name__)

# Initialize Prometheus metrics
metrics = PrometheusMetrics(app)
# Static information as metric
metrics.info('app_info', 'Application info', version='1.0.0')
# Track requests by endpoint
metrics.register_default(
    metrics.counter(
        'by_path_counter', 'Request count by request paths',
        labels={'path': lambda: request.path}
    )
)
# Custom metrics
counter_value = metrics.gauge('counter_value', 'Current counter value')
counter_increments = metrics.counter('counter_increments', 'Number of counter increments')

# Add request_id to each request
@app.before_request
def before_request():
    g.request_id = str(uuid.uuid4())
    logger.info(f"Request started: {request.method} {request.path}", 
                extra={"method": request.method, "path": request.path, "request_id": g.request_id})

@app.after_request
def after_request(response):
    logger.info(f"Request completed: {request.method} {request.path} {response.status_code}",
                extra={"method": request.method, "path": request.path, 
                       "status_code": response.status_code, "request_id": g.request_id})
    return response

# Database configuration
db_user = os.environ.get('DB_USER', 'postgres')
db_password = os.environ.get('DB_PASSWORD', 'postgres')
db_host = os.environ.get('DB_HOST', 'postgres')
db_port = os.environ.get('DB_PORT', '5432')
db_name = os.environ.get('DB_NAME', 'counter_db')

app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Counter model
class Counter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.Integer, default=0)

    def __repr__(self):
        return f'<Counter {self.value}>'

# Initialize database with retry logic
def initialize_database():
    max_retries = 5
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            logger.info(f"Attempting to connect to database (attempt {retry_count + 1}/{max_retries})",
                       extra={"retry_count": retry_count, "max_retries": max_retries})
            with app.app_context():
                db.create_all()
                
                # Check if counter exists, if not create it
                counter = Counter.query.first()
                if not counter:
                    logger.info("Creating initial counter", extra={"action": "create_counter"})
                    counter = Counter(value=0)
                    db.session.add(counter)
                    db.session.commit()
                    # Set initial metric value
                    counter_value.set(0)
            
            logger.info("Database initialization successful", extra={"status": "success"})
            return True
        except Exception as e:
            retry_count += 1
            logger.error(f"Database connection failed: {str(e)}", 
                        extra={"error": str(e), "retry_count": retry_count})
            if retry_count < max_retries:
                wait_time = 2 ** retry_count  # Exponential backoff
                logger.info(f"Retrying in {wait_time} seconds", 
                           extra={"wait_time": wait_time, "retry_count": retry_count})
                time.sleep(wait_time)
            else:
                logger.error("Max retries reached. Database initialization failed", 
                            extra={"status": "failed", "max_retries": max_retries})
                return False

# Initialize database on startup
initialize_database()

# Create a function to initialize the database on first request
def initialize_on_first_request():
    try:
        with app.app_context():
            db.create_all()
            counter = Counter.query.first()
            if not counter:
                logger.info("Creating initial counter on first request", extra={"action": "create_counter_first_request"})
                counter = Counter(value=0)
                db.session.add(counter)
                db.session.commit()
                # Set initial metric value
                counter_value.set(0)
            else:
                # Update metric with current counter value
                counter_value.set(counter.value)
    except Exception as e:
        logger.error(f"Error initializing database on first request: {str(e)}", extra={"error": str(e)})

# Register the function to run before the first request
app.before_request_funcs.setdefault(None, []).append(initialize_on_first_request)

# Routes
@app.route('/')
def index():
    logger.info("Serving index page", extra={"endpoint": "index"})
    return render_template('index.html')

@app.route('/health')
def health_check():
    try:
        # Check database connection
        Counter.query.first()
        logger.info("Health check successful", extra={"status": "healthy"})
        # Return a manually formatted JSON to ensure proper formatting
        return '{"status": "healthy", "database": "connected"}', 200, {'Content-Type': 'application/json'}
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}", extra={"status": "unhealthy", "error": str(e)})
        return '{"status": "unhealthy", "database": "disconnected", "error": "' + str(e) + '"}', 500, {'Content-Type': 'application/json'}

# API endpoints
@app.route('/api/counter', methods=['GET'])
def get_counter():
    try:
        counter = Counter.query.first()
        logger.info(f"Counter value retrieved: {counter.value}", extra={"counter_value": counter.value})
        # Update metric
        counter_value.set(counter.value)
        return jsonify({'value': counter.value})
    except Exception as e:
        logger.error(f"Error retrieving counter: {str(e)}", extra={"error": str(e)})
        return jsonify({'error': str(e)}), 500

@app.route('/api/counter/increment', methods=['POST'])
def increment_counter():
    try:
        counter = Counter.query.first()
        counter.value += 1
        db.session.commit()
        logger.info(f"Counter incremented to: {counter.value}", extra={"counter_value": counter.value})
        # Update metrics
        counter_value.set(counter.value)
        counter_increments.inc()
        return jsonify({'value': counter.value})
    except Exception as e:
        logger.error(f"Error incrementing counter: {str(e)}", extra={"error": str(e)})
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
