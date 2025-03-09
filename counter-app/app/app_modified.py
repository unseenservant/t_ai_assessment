import os
import time
from flask import Flask, jsonify, request, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import OperationalError

app = Flask(__name__)

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
            print(f"Attempting to connect to database (attempt {retry_count + 1}/{max_retries})...")
            with app.app_context():
                db.create_all()
                
                # Check if counter exists, if not create it
                counter = Counter.query.first()
                if not counter:
                    print("Creating initial counter...")
                    counter = Counter(value=0)
                    db.session.add(counter)
                    db.session.commit()
            
            print("Database initialization successful!")
            return True
        except Exception as e:
            retry_count += 1
            print(f"Database connection failed: {e}")
            if retry_count < max_retries:
                wait_time = 2 ** retry_count  # Exponential backoff
                print(f"Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                print("Max retries reached. Database initialization failed.")
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
                counter = Counter(value=0)
                db.session.add(counter)
                db.session.commit()
    except Exception as e:
        print(f"Error initializing database on first request: {e}")

# Register the function to run before the first request
app.before_request_funcs.setdefault(None, []).append(initialize_on_first_request)

# Routes
@app.route('/')
def index():
    return render_template('index.html')

# API endpoints
@app.route('/api/counter', methods=['GET'])
def get_counter():
    counter = Counter.query.first()
    return jsonify({'value': counter.value})

@app.route('/api/counter/increment', methods=['POST'])
def increment_counter():
    counter = Counter.query.first()
    counter.value += 1
    db.session.commit()
    return jsonify({'value': counter.value})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
