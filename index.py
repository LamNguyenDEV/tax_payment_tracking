from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

# Path to your SQLite database
DATABASE = 'example.db'

# Function to get a database connection
def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row  # This allows accessing columns by name
    return conn

# Initialize the database (for demo purposes)
def init_db():
    with app.app_context():
        db = get_db()
        db.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT NOT NULL,
                        email TEXT NOT NULL)''')
        db.commit()

# Home route to display users
@app.route('/')
def index():
    db = get_db()
    cur = db.execute('SELECT * FROM users')
    users = cur.fetchall()
    return render_template('index.html', users=users)

# Add user route (using POST method to add data)
@app.route('/add', methods=['POST'])
def add_user():
    username = request.form['username']
    email = request.form['email']

    db = get_db()
    db.execute('INSERT INTO users (username, email) VALUES (?, ?)', (username, email))
    db.commit()

    return redirect('/')

# Run the Flask application
if __name__ == '__main__':
    init_db()  # Initialize the database on startup
    app.run(debug=True)
