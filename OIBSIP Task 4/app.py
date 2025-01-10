from flask import Flask, render_template, request, flash, redirect, url_for, session
import sqlite3
from flask_sqlalchemy import SQLAlchemy
from functools import wraps
from flask_bcrypt import Bcrypt

app = Flask(__name__)

app.secret_key = '5f2b8d7681a82f9db9e12af30ed4cb57'

# Configure the SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'  
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False          

# Initialize SQLAlchemy
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
from werkzeug.security import generate_password_hash, check_password_hash

# User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)  # Hashes can be long

    def set_password(self, password):
        """Hash the password and store it."""
        self.password = generate_password_hash(password)

    def check_password(self, password):
        """Check if the provided password matches the stored hash."""
        return check_password_hash(self.password, password)

@app.route('/')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if not username or not password:
            flash("Username and Password are required!", "error")
            return redirect('/register')

        
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash("Username already exists. Please choose a different one.", "error")
            return redirect('/register')

        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        new_user = User(username=username, password=hashed_password)

        try:
            db.session.add(new_user)
            db.session.commit()
            flash("Registration successful! Please log in.", "success")
            return redirect('/login')
        except Exception as e:
            flash("An error occurred during registration. Please try again.", "error")
            print(f"Error: {e}")  # Log the error for debugging
            return redirect('/register')

    return render_template('register.html')



@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username') 
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()
        if user and bcrypt.check_password_hash(user.password, password):
            session['username'] = username
            
            return redirect('/dashboard')
        else:
            flash("Invalid username or password.", "error")
            return render_template('login.html')

    return render_template('login.html')


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            flash('You must be logged in to access this page.', 'error')
            return redirect('/login')
        return f(*args, **kwargs)
    return decorated_function


@app.route('/home')
def home():
    return "<h1>Welcome to the Home Page!</h1>"

@app.route('/dashboard')
@login_required
def dashboard():    
    if 'username' in session:
        print(f"Logged in as: {session['username']}")  # Debugging
        return render_template('dashboard.html')
    else:
        flash("Please log in to access the dashboard.", "error")
        return redirect('/login')


@app.route('/logout')
def logout():
    session.pop('username', None)  
    flash("You have been logged out.", "info")
    return redirect('/login')

if __name__ == '__main__':
    app.run(debug=True)
