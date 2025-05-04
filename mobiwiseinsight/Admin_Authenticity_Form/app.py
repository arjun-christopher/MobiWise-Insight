from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, get_flashed_messages
import pyodbc
from datetime import datetime

app = Flask(__name__)
app.secret_key = '****MASKED****'

# Database connection setup
dsn = '****MASKED****'  # Replace with your DSN name
user_name = '****MASKED****'
password = '****MASKED****'

role = ""
id = ""

def get_db_connection():
    return pyodbc.connect(f"DSN={dsn};UID={user_name};PWD={password}", timeout=10)

@app.route('/')
def user():
    flash_messages = {category: message for category, message in get_flashed_messages(with_categories=True)}
    return render_template('admin.html', flash_messages=flash_messages)

@app.route('/get_admin_role', methods=['GET'])
def get_admin_role():

    if not role:
        return jsonify({"error": "Not logged in"}), 401  # Unauthorized access

    return jsonify({"role": role, "id": id}), 200

# Admin Login Route
@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    error_message = None  # Initialize an empty error message

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT AdminID, Name, Role FROM Admins WHERE Email=? AND Password=?", (email, password))
        admin = cursor.fetchone()
        conn.close()
        
        if admin:
            session['admin_id'] = admin[0]
            session['admin_name'] = admin[1]
            session['admin_role'] = admin[2]

            global role, id
            role = admin[2]
            id = admin[0]
            
            # Update last login time
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("UPDATE Admins SET LastLogin=? WHERE AdminID=?", (datetime.now(), admin[0]))
            conn.commit()
            conn.close()
            
            return redirect(url_for('admin_dashboard'))  # Redirects to the dashboard
        else:
            error_message = "Invalid credentials. Please try again."  # Set error message

    return render_template('admin.html', error_message=error_message)  # Pass error to template


# Admin Dashboard Route
@app.route('/admin_dashboard')
def admin_dashboard():
    if 'admin_id' not in session:
        return redirect('/admin_login')
    return render_template('dashboard.html', admin_name=session['admin_name'], admin_role=session['admin_role'])

# Admin Logout Route
@app.route('/admin_logout')
def admin_logout():
    session.clear()
    flash('Logged out successfully.', 'success')
    return redirect('/admin_login')

def start_admin():
    app.run(port=5003, debug=True)
