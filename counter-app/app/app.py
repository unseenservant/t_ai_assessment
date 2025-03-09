import os
from flask import Flask, jsonify, request, render_template
from flask_sqlalchemy import SQLAlchemy

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

# Create tables and initialize counter if it doesn't exist
@app.before_first_request
def initialize_database():
    db.create_all()
    counter = Counter.query.first()
    if not counter:
        counter = Counter(value=0)
        db.session.add(counter)
        db.session.commit()

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
