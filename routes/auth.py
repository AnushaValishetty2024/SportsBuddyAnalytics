from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models import User, mysql
import re

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/')
def home():
    user = None
    if 'user_id' in session:
        user = User.get_by_id(session['user_id'])
    return render_template('home.html', current_user=user)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        # Basic input validation
        if not name or not email or not password:
            flash('All fields are required.', 'danger')
            return render_template('register.html')

        if len(name) < 2:
            flash('Name must be at least 2 characters.', 'danger')
            return render_template('register.html')

        if not re.match(r'^[^@]+@[^@]+\.[^@]+$', email):
            flash('Please enter a valid email address.', 'danger')
            return render_template('register.html')

        if len(password) < 6:
            flash('Password must be at least 6 characters.', 'danger')
            return render_template('register.html')

        # Check if email already exists
        existing_user = User.find_by_email(email)
        if existing_user:
            flash('An account with this email already exists.', 'danger')
            return render_template('register.html')

        # Create user
        try:
            user_id = User.create(name, email, password)
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            flash('An error occurred during registration. Please try again.', 'danger')
            return render_template('register.html')

    return render_template('register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        if not email or not password:
            flash('Please fill in all fields.', 'danger')
            return render_template('login.html')

        user = User.find_by_email(email)
        if not user or not User.verify_password(user['password_hash'], password):
            flash('Invalid email or password.', 'danger')
            return render_template('login.html')

        session['user_id'] = user['id']
        session['user_name'] = user['name']
        flash('Login successful! Welcome back.', 'success')
        return redirect(url_for('dashboard.dashboard'))

    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.home'))