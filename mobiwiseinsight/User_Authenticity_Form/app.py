from flask import Flask, render_template, request, redirect, url_for, flash, get_flashed_messages, jsonify, make_response
import pyodbc
import random
import smtplib
from datetime import datetime, timedelta
from email.mime.text import MIMEText
import jwt
from functools import wraps

from .programs.sms import send_sms

# Initialize Flask app
app = Flask(__name__)
app.secret_key = '****MASKED****'  # Required for flashing messages

SECRET_KEY = "****MASKED****"  # Keep this secure

# Database connection setup
dsn = '****MASKED****'  # Replace with your DSN name
user_name = '****MASKED****'
password = '****MASKED****'
connection = pyodbc.connect(f"DSN={dsn};UID={user_name};PWD={password}", timeout=10)

# SMTP configuration
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
SENDER_EMAIL = '****MASKED****'  # Update with your email
SENDER_PASSWORD = '****MASKED****'  # App-specific password

# Generate JWT token
def generate_token(username, email, phone):
    payload = {
        "username": username,
        "email": email,
        "phone": phone,
        "exp": datetime.utcnow() + timedelta(days=7)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

@app.route('/')
def user():
    flash_messages = {category: message for category, message in get_flashed_messages(with_categories=True)}
    return render_template('login.html', flash_messages=flash_messages)


@app.route('/signuppage')
def signuppage():
    flash_messages = {category: message for category, message in get_flashed_messages(with_categories=True)}
    return render_template('signup.html', flash_messages=flash_messages)

@app.route('/login', methods=['POST'])
def login():
    user_input = request.form['username']  # Can be either username or email
    password = request.form['password']

    cursor = connection.cursor()
    try:
        # Check if the input is an email
        if '@' in user_input and '.' in user_input:
            query = "SELECT * FROM users WHERE email = ? AND password = ?"
        else:
            query = "SELECT * FROM users WHERE username = ? AND password = ?"

        cursor.execute(query, (user_input, password))
        user = cursor.fetchone()

        if user:
            print(user)
            cursor.execute("UPDATE users SET lastlogin = SYSDATE WHERE username = ?", (user[1],))
            print("Login successful")
            connection.commit()

            # On successful login
            token = generate_token(user[1], user[2], user[3])
            response = make_response(redirect("http://127.0.0.1:5001/"))  # or your dashboard page
            response.set_cookie("jwt", token, httponly=True, max_age=86400)
            return response

            # return redirect(url_for('user'))
        else:
            flash('Invalid username/email or password!', 'login_error')
            return redirect(url_for('user'))
    except pyodbc.Error as e:
        flash(f"Database error: {str(e)}", 'login_error')
        return redirect(url_for('user'))
    finally:
        cursor.close()


@app.route('/signup', methods=['POST'])
def signup():
    username = request.form['newUsername']
    email = request.form['email']
    password = request.form['newPassword']
    confirm_password = request.form['confirmPassword']
    phone = request.form['phone']

    cursor = connection.cursor()
    try:
        # Check if username already exists
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        if cursor.fetchone():
            flash('Username already exists!', 'signup_error')
            return redirect(url_for('signuppage'))

        # Check if email already exists
        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        if cursor.fetchone():
            flash('Email already exists!', 'signup_error')
            return redirect(url_for('signuppage'))

        # Validate password length
        if len(password) < 8 or len(password) > 16:
            flash("Password must be between 8 and 16 characters!", 'signup_error')
            return redirect(url_for('signuppage'))

        # Validate passwords match
        if password != confirm_password:
            flash("Passwords do not match!", 'signup_error')
            return redirect(url_for('signuppage'))
        
        if not phone:
            flash("Phone number is required!", 'signup_error')
            return redirect(url_for('signuppage'))

        # Insert new user into database
        cursor.execute("""
            INSERT INTO users (userid, username, email, password, createdat, phone)
            VALUES (seq_user_id.NEXTVAL, ?, ?, ?, ?, ?)
        """, (username, email, password, datetime.now(), phone))
        connection.commit()
        print("Signup successful")

        # On successful login
        token = generate_token(username, email, phone)
        response = make_response(redirect("http://127.0.0.1:5001/"))  # or your dashboard page
        response.set_cookie("jwt", token, httponly=True, max_age=86400)
        return response
    
        # return redirect(url_for('signuppage'))

    except pyodbc.Error as e:
        flash(f"Database error: {str(e)}", 'signup_error')
        return redirect(url_for('signuppage'))
    finally:
        cursor.close()

@app.route('/change_password', methods=['POST'])
def change_password():
    try:
        data = request.get_json()
        username_or_email = data.get('usernameOrEmail')
        current_password = data.get('currentPassword')
        new_password = data.get('newPassword')
        confirm_new_password = data.get('confirmNewPassword')

        cursor = connection.cursor()

        # Check if username or email exists in the database
        cursor.execute("SELECT username, email, password FROM users WHERE username = ? OR email = ?", (username_or_email, username_or_email))
        user_record = cursor.fetchone()

        if not user_record:
            return jsonify({"error": "User does not exist."}), 400

        db_password = user_record[2]

        # Verify current password
        if current_password != db_password:
            return jsonify({"error": "Current password is incorrect."}), 400
        
        if len(new_password) < 8 or len(new_password) > 16:
            return jsonify({"error": "Invalid password length."}), 400

        # Verify new password and confirm password match
        if new_password != confirm_new_password:
            return jsonify({"error": "New password and confirm password do not match."}), 400

        # Update the database with the new password
        cursor.execute("""
            UPDATE users
            SET prev_password = password, password = ?
            WHERE username = ? OR email = ?
        """, (new_password, username_or_email, username_or_email))

        connection.commit()

        return jsonify({"success": "Password updated successfully."})

    except pyodbc.Error as e:
        app.logger.error(f"Database error: {str(e)}")
        return jsonify({"error": "Database error occurred."}), 500
    except Exception as e:
        app.logger.error(f"Unexpected error: {str(e)}")
        return jsonify({"error": "An unexpected error occurred."}), 500
    finally:
        if 'cursor' in locals():
            cursor.close()


otp_sent_time = {}  # To track the OTP resend time for each email

def send_email(recipient, subject, body):
    try:
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = SENDER_EMAIL
        msg['To'] = recipient

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(msg)
    except Exception as e:
        print(f"SMTP Error: {str(e)}")
        return False
    return True


@app.route('/request_otp', methods=['POST'])
def request_otp():
    data = request.json
    email = data.get('email')

    if not email:
        return jsonify({"error": "Email is required."}), 400

    cursor = connection.cursor()
    cursor.execute("SELECT username FROM users WHERE email = ?", (email,))
    user = cursor.fetchone()

    if not user:
        return jsonify({"error": "Email not found in database."}), 404

    # Check OTP resend timer
    now = datetime.now()
    if email in otp_sent_time and now < otp_sent_time[email] + timedelta(minutes=2):
        return jsonify({"error": "OTP resend is unavailable. Please wait 2 minutes."}), 403

    # Generate OTP
    otp = random.randint(100000, 999999)
    cursor.execute("UPDATE users SET otp = ? WHERE email = ?", (otp, email))
    cursor.execute("SELECT phone FROM users WHERE email = ?", (email,))
    phone = cursor.fetchone()
    connection.commit()

    # Send OTP via email
    subject = "Your OTP for Password Reset"
    body = f"Your OTP is {otp}. It is valid for 2 minutes."
    if not send_email(email, subject, body):
        return jsonify({"error": "Failed to send OTP, through E-mail. Please try again later."}), 500
    
    if not send_sms(otp, phone):
        return jsonify({"error": "Failed to send OTP, through SMS. Please try again later."}), 500

    otp_sent_time[email] = now  # Update OTP sent time
    return jsonify({"success": "OTP sent successfully.", "otp": otp}), 200


@app.route('/validate_otp', methods=['POST'])
def validate_otp():
    data = request.json
    email = data.get('email')
    otp = data.get('otp')

    cursor = connection.cursor()
    try:
        cursor.execute("SELECT otp FROM users WHERE email = ?", (email,))
        result = cursor.fetchone()

        if not result or int(result[0]) != int(otp):
            return jsonify({"error": "Invalid or expired OTP."}), 400

        return jsonify({"success": "OTP verified successfully."}), 200
    except Exception as e:
        app.logger.error(f"Unexpected error during OTP validation: {str(e)}")
        return jsonify({"error": "An unexpected error occurred."}), 500
    finally:
        cursor.close()

@app.route('/update_password', methods=['POST'])
def update_password():
    data = request.json
    email = data.get('email')
    otp = data.get('otp')
    new_password = data.get('newPassword')
    confirm_password = data.get('confirmNewPassword')

    if new_password != confirm_password:
        return jsonify({"error": "Passwords do not match."}), 400

    cursor = connection.cursor()
    try:
        cursor.execute("SELECT otp, password FROM users WHERE email = ?", (email,))
        record = cursor.fetchone()

        if not record or int(record[0]) != int(otp):
            return jsonify({"error": "Invalid or expired OTP."}), 400

        # Update password and store the old one in prev_password
        cursor.execute(
            "UPDATE users SET password = ?, prev_password = ?, otp = NULL WHERE email = ?",
            (new_password, record[1], email)
        )
        connection.commit()

        return jsonify({"success": "Password updated successfully."}), 200
    except Exception as e:
        app.logger.error(f"Unexpected error during password update: {str(e)}")
        return jsonify({"error": "An unexpected error occurred."}), 500
    finally:
        cursor.close()

def start_user():
    app.run(port=5002, debug=True)
