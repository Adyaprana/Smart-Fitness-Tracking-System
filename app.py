import os
import sqlite3
from datetime import datetime, timedelta
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
import csv

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-in-production'
app.config['DATABASE'] = 'database.db'
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_SECURE'] = False
app.config['SESSION_COOKIE_HTTPONLY'] = True

# Initialize database
def init_db():
    conn = sqlite3.connect(app.config['DATABASE'])
    c = conn.cursor()
    
    # Users table
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        age INTEGER,
        gender TEXT,
        height REAL,
        weight REAL,
        goal TEXT
    )''')
    
    # Diet logs table
    c.execute('''CREATE TABLE IF NOT EXISTS diet_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        food_name TEXT NOT NULL,
        meal_type TEXT,
        calories REAL,
        protein REAL,
        carbs REAL,
        fats REAL,
        date TEXT,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )''')
    
    # Fitness logs table
    c.execute('''CREATE TABLE IF NOT EXISTS fitness_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        activity_type TEXT NOT NULL,
        duration INTEGER,
        calories_burned REAL,
        date TEXT,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )''')
    
    # Progress table
    c.execute('''CREATE TABLE IF NOT EXISTS progress (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        weight REAL,
        bmi REAL,
        date TEXT,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )''')
    
    # Food database table
    c.execute('''CREATE TABLE IF NOT EXISTS food_database (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        food_name TEXT NOT NULL,
        category TEXT,
        calories REAL,
        protein REAL,
        carbs REAL,
        fat REAL,
        serving_size INTEGER,
        serving_unit TEXT
    )''')
    
    conn.commit()
    conn.close()

# Load food database from CSV
def load_food_database():
    conn = sqlite3.connect(app.config['DATABASE'])
    c = conn.cursor()
    
    # Check if food database is already loaded
    c.execute('SELECT COUNT(*) FROM food_database')
    if c.fetchone()[0] > 0:
        conn.close()
        return
    
    try:
        csv_path = 'user_read_only_context/text_attachments/food_database-h6Hoc.csv'
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    calories = float(row['calories']) if row['calories'] else 0
                    protein = float(row['protein']) if row['protein'] else 0
                    carbs = float(row['carbs']) if row['carbs'] else 0
                    fat = float(row['fat']) if row['fat'] else 0
                    serving_size = int(row['serving_size']) if row['serving_size'] else 1
                    
                    c.execute('''INSERT INTO food_database 
                        (food_name, category, calories, protein, carbs, fat, serving_size, serving_unit)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                        (row['food_name'], row['category'], calories, protein, carbs, fat, serving_size, row['serving_unit']))
                except:
                    pass
        conn.commit()
    except Exception as e:
        print(f"Error loading food database: {e}")
    
    conn.close()

# Create demo users
def create_demo_users():
    conn = sqlite3.connect(app.config['DATABASE'])
    c = conn.cursor()
    
    demo_users = [
        ('adya21', 'adya21', 25, 'Female', 165, 65, 'fat loss'),
        ('demo22', 'demo22', 30, 'Male', 180, 80, 'muscle gain')
    ]
    
    for username, password, age, gender, height, weight, goal in demo_users:
        try:
            password_hash = generate_password_hash(password)
            c.execute('''INSERT INTO users (username, password_hash, age, gender, height, weight, goal)
                VALUES (?, ?, ?, ?, ?, ?, ?)''',
                (username, password_hash, age, gender, height, weight, goal))
        except sqlite3.IntegrityError:
            pass
    
    conn.commit()
    conn.close()

# Add demo data
def add_demo_data():
    conn = sqlite3.connect(app.config['DATABASE'])
    c = conn.cursor()
    
    # Get demo user IDs
    c.execute('SELECT id FROM users WHERE username = "adya21" LIMIT 1')
    result = c.fetchone()
    if not result:
        conn.close()
        return
    
    user_id = result[0]
    today = datetime.now().date()
    
    # Add 7 days of demo diet data
    diet_data = [
        ('Chicken Breast', 'Lunch', 202, 21.15, 7.34, 9.15),
        ('Brown Rice', 'Lunch', 124, 2.45, 25.89, 1.12),
        ('Salmon', 'Dinner', 232, 19.0, 0.0, 15.5),
        ('Broccoli', 'Dinner', 24, 2.35, 4.71, 0.0),
        ('Eggs', 'Breakfast', 136, 13.6, 0.0, 9.09),
        ('Whole Wheat Bread', 'Breakfast', 233, 11.6, 44.2, 2.33),
        ('Apple', 'Snack', 52, 0.0, 14.3, 0.65),
    ]
    
    for i in range(7):
        date = (today - timedelta(days=i)).isoformat()
        for food, meal_type, cal, prot, carb, fat in diet_data:
            try:
                c.execute('''INSERT INTO diet_logs 
                    (user_id, food_name, meal_type, calories, protein, carbs, fats, date)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                    (user_id, food, meal_type, cal, prot, carb, fat, date))
            except:
                pass
    
    # Add 7 days of demo fitness data
    fitness_data = [
        ('Running', 30, 350),
        ('Cycling', 45, 280),
        ('Gym', 60, 400),
        ('Swimming', 30, 320),
    ]
    
    for i in range(7):
        date = (today - timedelta(days=i)).isoformat()
        activity, duration, calories = fitness_data[i % len(fitness_data)]
        try:
            c.execute('''INSERT INTO fitness_logs 
                (user_id, activity_type, duration, calories_burned, date)
                VALUES (?, ?, ?, ?, ?)''',
                (user_id, activity, duration, calories, date))
        except:
            pass
    
    # Add 7 days of demo progress data
    for i in range(7):
        date = (today - timedelta(days=i)).isoformat()
        weight = 65 - (i * 0.1)
        bmi = weight / ((1.65) ** 2)
        try:
            c.execute('''INSERT INTO progress (user_id, weight, bmi, date)
                VALUES (?, ?, ?, ?)''',
                (user_id, weight, bmi, date))
        except:
            pass
    
    conn.commit()
    conn.close()

@app.before_request
def before_request():
    if 'user_id' in session:
        pass

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        conn = sqlite3.connect(app.config['DATABASE'])
        c = conn.cursor()
        c.execute('SELECT id, password_hash FROM users WHERE username = ?', (username,))
        user = c.fetchone()
        conn.close()
        
        if user and check_password_hash(user[1], password):
            session['user_id'] = user[0]
            session['username'] = username
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'message': 'Invalid credentials'}), 401
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    return render_template('dashboard.html')

@app.route('/diet')
def diet():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    return render_template('diet.html')

@app.route('/fitness')
def fitness():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    return render_template('fitness.html')

@app.route('/progress')
def progress():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    return render_template('progress.html')

@app.route('/profile')
def profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    return render_template('profile.html')

# API Routes
@app.route('/api/dashboard-data')
def get_dashboard_data():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    user_id = session['user_id']
    today = datetime.now().date().isoformat()
    
    conn = sqlite3.connect(app.config['DATABASE'])
    c = conn.cursor()
    
    # Get user info (username, height, weight, goal)
    c.execute('SELECT username, height, weight, goal FROM users WHERE id = ?', (user_id,))
    row = c.fetchone()
    username = row[0] if row else 'User'
    height = row[1] if row and row[1] else 170
    weight = row[2] if row and row[2] else 70
    goal = row[3] if row and row[3] else 'maintenance'
    
    # Today's calories and macros
    c.execute('''SELECT SUM(calories), SUM(protein), SUM(carbs), SUM(fats)
                 FROM diet_logs WHERE user_id = ? AND date = ?''', (user_id, today))
    diet_row = c.fetchone()
    calories_intake = (diet_row[0] or 0)
    protein = (diet_row[1] or 0)
    carbs = (diet_row[2] or 0)
    fats = (diet_row[3] or 0)
    
    # Today's calories burned
    c.execute('SELECT SUM(calories_burned) FROM fitness_logs WHERE user_id = ? AND date = ?', (user_id, today))
    calories_burned = c.fetchone()[0] or 0
    
    # Latest weight and BMI
    c.execute('SELECT weight, bmi FROM progress WHERE user_id = ? ORDER BY date DESC LIMIT 1', (user_id,))
    progress_data = c.fetchone()
    current_weight = progress_data[0] if progress_data else weight
    bmi = weight / ((height / 100) ** 2) if height else 0
    current_bmi = progress_data[1] if progress_data else bmi
    
    # Last 7 days calories for Intake Rhythm
    weekly_intake = []
    for i in range(6, -1, -1):
        d = (datetime.now().date() - timedelta(days=i)).isoformat()
        c.execute('SELECT SUM(calories) FROM diet_logs WHERE user_id = ? AND date = ?', (user_id, d))
        weekly_intake.append(round(c.fetchone()[0] or 0, 0))
    
    conn.close()
    
    return jsonify({
        'username': username,
        'calories_intake': round(calories_intake, 2),
        'calories_burned': round(calories_burned, 2),
        'bmi': round(current_bmi, 1),
        'weight': round(current_weight, 1),
        'goal': goal,
        'protein': round(protein, 0),
        'carbs': round(carbs, 0),
        'fats': round(fats, 0),
        'weekly_intake': weekly_intake
    })

@app.route('/api/food-search')
def food_search():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    query = request.args.get('q', '').lower()
    
    conn = sqlite3.connect(app.config['DATABASE'])
    c = conn.cursor()
    c.execute('''SELECT id, food_name, calories, protein, carbs, fat, category 
        FROM food_database WHERE LOWER(food_name) LIKE ? LIMIT 20''',
        (f'%{query}%',))
    foods = [dict(zip(['id', 'food_name', 'calories', 'protein', 'carbs', 'fat', 'category'], row)) for row in c.fetchall()]
    conn.close()
    
    return jsonify(foods)

@app.route('/api/add-diet', methods=['POST'])
def add_diet():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.get_json()
    user_id = session['user_id']
    
    conn = sqlite3.connect(app.config['DATABASE'])
    c = conn.cursor()
    c.execute('''INSERT INTO diet_logs 
        (user_id, food_name, meal_type, calories, protein, carbs, fats, date)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
        (user_id, data['food_name'], data['meal_type'], data['calories'], 
         data['protein'], data['carbs'], data['fats'], datetime.now().date().isoformat()))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

@app.route('/api/add-fitness', methods=['POST'])
def add_fitness():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.get_json()
    user_id = session['user_id']
    
    # Get user weight for calorie calculation
    conn = sqlite3.connect(app.config['DATABASE'])
    c = conn.cursor()
    c.execute('SELECT weight FROM users WHERE id = ?', (user_id,))
    weight = c.fetchone()[0] or 70
    
    # MET values for activities
    met_values = {
        'Running': 9.8,
        'Walking': 3.5,
        'Cycling': 7.5,
        'Swimming': 8.0,
        'Football': 10.0,
        'Cricket': 6.0,
        'Gym': 6.0,
        'Yoga': 3.0
    }
    
    met = met_values.get(data['activity_type'], 5.0)
    duration = data['duration']
    calories_burned = met * weight * (duration / 60)
    
    c.execute('''INSERT INTO fitness_logs 
        (user_id, activity_type, duration, calories_burned, date)
        VALUES (?, ?, ?, ?, ?)''',
        (user_id, data['activity_type'], duration, calories_burned, datetime.now().date().isoformat()))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'calories_burned': round(calories_burned, 2)})

@app.route('/api/diet-logs')
def get_diet_logs():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    user_id = session['user_id']
    date = request.args.get('date', datetime.now().date().isoformat())
    
    conn = sqlite3.connect(app.config['DATABASE'])
    c = conn.cursor()
    c.execute('''SELECT id, food_name, meal_type, calories, protein, carbs, fats, date 
        FROM diet_logs WHERE user_id = ? AND date = ? ORDER BY date DESC''',
        (user_id, date))
    logs = [dict(zip(['id', 'food_name', 'meal_type', 'calories', 'protein', 'carbs', 'fats', 'date'], row)) for row in c.fetchall()]
    conn.close()
    
    return jsonify(logs)

@app.route('/api/fitness-logs')
def get_fitness_logs():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    user_id = session['user_id']
    date = request.args.get('date', datetime.now().date().isoformat())
    
    conn = sqlite3.connect(app.config['DATABASE'])
    c = conn.cursor()
    c.execute('''SELECT id, activity_type, duration, calories_burned, date 
        FROM fitness_logs WHERE user_id = ? AND date = ? ORDER BY date DESC''',
        (user_id, date))
    logs = [dict(zip(['id', 'activity_type', 'duration', 'calories_burned', 'date'], row)) for row in c.fetchall()]
    conn.close()
    
    return jsonify(logs)

@app.route('/api/delete-diet/<int:diet_id>', methods=['DELETE'])
def delete_diet(diet_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    user_id = session['user_id']
    
    conn = sqlite3.connect(app.config['DATABASE'])
    c = conn.cursor()
    # Verify the diet log belongs to the user
    c.execute('SELECT id FROM diet_logs WHERE id = ? AND user_id = ?', (diet_id, user_id))
    if not c.fetchone():
        conn.close()
        return jsonify({'error': 'Not found'}), 404
    
    c.execute('DELETE FROM diet_logs WHERE id = ? AND user_id = ?', (diet_id, user_id))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

@app.route('/api/delete-fitness/<int:fitness_id>', methods=['DELETE'])
def delete_fitness(fitness_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    user_id = session['user_id']
    
    conn = sqlite3.connect(app.config['DATABASE'])
    c = conn.cursor()
    # Verify the fitness log belongs to the user
    c.execute('SELECT id FROM fitness_logs WHERE id = ? AND user_id = ?', (fitness_id, user_id))
    if not c.fetchone():
        conn.close()
        return jsonify({'error': 'Not found'}), 404
    
    c.execute('DELETE FROM fitness_logs WHERE id = ? AND user_id = ?', (fitness_id, user_id))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

@app.route('/api/progress-data')
def get_progress_data():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    user_id = session['user_id']
    
    conn = sqlite3.connect(app.config['DATABASE'])
    c = conn.cursor()
    c.execute('''SELECT weight, bmi, date FROM progress WHERE user_id = ? 
        ORDER BY date DESC LIMIT 30''',
        (user_id,))
    data = [dict(zip(['weight', 'bmi', 'date'], row)) for row in c.fetchall()]
    conn.close()
    
    return jsonify(data[::-1])

@app.route('/api/user-profile')
def get_user_profile():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    user_id = session['user_id']
    
    conn = sqlite3.connect(app.config['DATABASE'])
    c = conn.cursor()
    c.execute('SELECT username, age, gender, height, weight, goal FROM users WHERE id = ?', (user_id,))
    user = c.fetchone()
    conn.close()
    
    if user:
        return jsonify({
            'username': user[0],
            'age': user[1],
            'gender': user[2],
            'height': user[3],
            'weight': user[4],
            'goal': user[5]
        })
    
    return jsonify({'error': 'User not found'}), 404

@app.route('/api/update-profile', methods=['POST'])
def update_profile():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.get_json()
    user_id = session['user_id']
    
    conn = sqlite3.connect(app.config['DATABASE'])
    c = conn.cursor()
    c.execute('''UPDATE users SET age = ?, gender = ?, height = ?, weight = ?, goal = ? WHERE id = ?''',
        (data['age'], data['gender'], data['height'], data['weight'], data['goal'], user_id))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

if __name__ == '__main__':
    init_db()
    load_food_database()
    create_demo_users()
    add_demo_data()
    app.run(debug=True)
