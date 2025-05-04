from flask import Flask, render_template, request, get_flashed_messages, jsonify, redirect
import pyodbc
from datetime import datetime
from decimal import Decimal
import sys
import os
import requests

sys.path.append(os.path.abspath(r"E:\MobiWise Insight - Mini-Project\Website\Admin_Authenticity_Form"))

# API URL of session handler
SESSION_API_URL = "http://127.0.0.1:5003/get_admin_role"

# Initialize Flask app
app = Flask(__name__)
app.secret_key = '****MASKED****'  

# Database connection setup
dsn = '****MASKED****'  
user = '****MASKED****'
password = '****MASKED****'
conn = pyodbc.connect(f"DSN={dsn};UID={user};PWD={password}", timeout=10)


@app.route('/')
def admin_table():
    flash_messages = {category: message for category, message in get_flashed_messages(with_categories=True)}
    return render_template('admin_form.html', flash_messages=flash_messages)

@app.route('/get_admin_role', methods=['GET'])
def get_admin_role():
    """
    Fetch the logged-in admin's role and return it as JSON.
    """
    response = requests.get(SESSION_API_URL)
    if response.status_code == 200:
        admin_role = response.json().get("role")
        print(f"Admin role: {admin_role}")
        return jsonify({"role": admin_role}), 200

@app.route('/get_next_admin_id', methods=['GET'])
def get_next_admin_id():
    try:
        cursor = conn.cursor()

        # Query to find the next available AdminID (assuming IDs are sequential)
        cursor.execute("""
            SELECT NVL(MAX(AdminID), 0) + 1 AS next_id
            FROM Admins
        """)
        result = cursor.fetchone()
        next_id = result[0] if result else 1  # Default to 1 if no records exist
        print(f"Next Admin ID: {next_id}")

        cursor.close()
        return jsonify({"next_id": next_id})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/fetch_admin', methods=['POST'])
def fetch_admin():
    data = request.get_json()
    admin_id = data.get('admin_id')

    cursor = conn.cursor()
    try:
        # Check if the Admin ID exists in the Admins table
        cursor.execute("SELECT * FROM Admins WHERE AdminID = ?", (admin_id,))
        record = cursor.fetchone()

        if record:
            # Get column names from the cursor description
            columns = [column[0] for column in cursor.description]
            response_data = dict(zip(columns, record))

            # Debugging: Log the fetched data
            print(f"Record fetched: {record}")
            print(f"Columns fetched: {columns}")

            # Convert fields if necessary
            response_data['CreatedAt'] = response_data.get('CreatedAt', '').strftime('%Y-%m-%d') if response_data.get('CreatedAt') else None
            response_data['LastLogin'] = response_data.get('LastLogin', '').strftime('%Y-%m-%d') if response_data.get('LastLogin') else None

            return jsonify(response_data), 200
        else:
            return jsonify({"error": f"No record found for Admin ID: {admin_id}"}), 404

    except pyodbc.Error as e:
        return jsonify({"error": f"Database error: {str(e)}"}), 500
    finally:
        cursor.close()

@app.route('/save_admin', methods=['POST'])
def save_admin():
    """
    Save a record into the Admins table. 
    If the AdminID already exists, return an error.
    """
    data = request.get_json()

    # Extract form fields
    admin_id = data.get('admin_id')
    name = data.get('name')
    password = data.get('password')
    email = data.get('email')
    phone = data.get('phone')
    role = data.get('role')
    status = data.get('status')
    created_at = data.get('created_at')
    last_login = data.get('last_login')

    if not all([admin_id, name, password, email, phone, role, status]):
        return jsonify({"error": "All required fields must be filled."}), 400

    cursor = conn.cursor()
    try:
        # Check if the AdminID already exists in the Admins table
        cursor.execute("SELECT 1 FROM Admins WHERE AdminID = ?", (admin_id,))
        if cursor.fetchone():
            return jsonify({"error": f"Admin ID {admin_id} already exists."}), 409

        # Insert the new admin record into the Admins table
        cursor.execute("""
            INSERT INTO Admins (AdminID, Name, Password, Email, Phone, Role, Status, CreatedAt, LastLogin)
            VALUES (?, ?, ?, ?, ?, ?, ?, TO_DATE(?, 'YYYY-MM-DD'), TO_DATE(?, 'YYYY-MM-DD'))
        """, (admin_id, name, password, email, phone, role, status, created_at, last_login))
        conn.commit()

        return jsonify({"success": f"Admin ID {admin_id} successfully saved."}), 200

    except pyodbc.Error as e:
        conn.rollback()
        return jsonify({"error": f"Database error: {str(e)}"}), 500
    finally:
        cursor.close()


@app.route('/fetch_next_admin', methods=['POST'])
def fetch_next_admin():
    """
    Fetch the next admin record based on the current AdminID.
    """
    data = request.get_json()
    current_id = data.get('admin_id')

    if not current_id:
        return jsonify({"error": "Current Admin ID is not provided."}), 400

    cursor = conn.cursor()
    try:
        # Query for the next admin record
        cursor.execute("""
            SELECT * FROM (
                SELECT * FROM Admins
                WHERE AdminID > ?
                ORDER BY AdminID ASC
            ) WHERE ROWNUM = 1
        """, (current_id,))
        record = cursor.fetchone()

        if record:
            # Get column names and prepare response
            columns = [column[0] for column in cursor.description]
            response_data = dict(zip(columns, record))

            # Convert date fields to string format
            response_data['CreatedAt'] = response_data.get('CreatedAt', '').strftime('%Y-%m-%d') if response_data.get('CreatedAt') else None
            response_data['LastLogin'] = response_data.get('LastLogin', '').strftime('%Y-%m-%d') if response_data.get('LastLogin') else None

            return jsonify(response_data), 200
        else:
            return jsonify({"error": "No next record found in the Admins table."}), 404

    except pyodbc.Error as e:
        return jsonify({"error": f"Database error: {str(e)}"}), 500
    finally:
        cursor.close()


@app.route('/fetch_previous_admin', methods=['POST'])
def fetch_previous_admin():
    """
    Fetch the previous admin record based on the current AdminID.
    """
    data = request.get_json()
    current_id = data.get('admin_id')

    if not current_id:
        return jsonify({"error": "Current Admin ID is not provided."}), 400

    cursor = conn.cursor()
    try:
        # Query for the previous admin record
        cursor.execute("""
            SELECT * FROM (
                SELECT * FROM Admins
                WHERE AdminID < ?
                ORDER BY AdminID DESC
            ) WHERE ROWNUM = 1
        """, (current_id,))
        record = cursor.fetchone()

        if record:
            # Get column names and prepare response
            columns = [column[0] for column in cursor.description]
            response_data = dict(zip(columns, record))

            # Convert date fields to string format
            response_data['CreatedAt'] = response_data.get('CreatedAt', '').strftime('%Y-%m-%d') if response_data.get('CreatedAt') else None
            response_data['LastLogin'] = response_data.get('LastLogin', '').strftime('%Y-%m-%d') if response_data.get('LastLogin') else None

            return jsonify(response_data), 200
        else:
            return jsonify({"error": "No previous record found in the Admins table."}), 404

    except pyodbc.Error as e:
        return jsonify({"error": f"Database error: {str(e)}"}), 500
    finally:
        cursor.close()

@app.route('/update_admin', methods=['POST'])
def update_admin():
    data = request.get_json()
    admin_id = data.get('admin_id')
    name = data.get('name')
    password = data.get('password')
    email = data.get('email')
    phone = data.get('phone')
    role = data.get('role')
    status = data.get('status')
    created_at = data.get('created_at')
    last_login = data.get('last_login')

    cursor = conn.cursor()
    try:
        # Check if the Admin ID exists in the Admins table
        cursor.execute("SELECT * FROM Admins WHERE AdminID = ?", (admin_id,))
        admin_record = cursor.fetchone()

        if not admin_record:
            return jsonify({"error": f"Admin ID {admin_id} does not exist in the Admins table."}), 404

        # Convert record to a dictionary
        column_names = [desc[0] for desc in cursor.description]
        current_values = dict(zip(column_names, admin_record))

        # Compare received data with the existing admin record
        updates = {
            "Name": name,
            "Password": password,
            "Email": email,
            "Phone": phone,
            "Role": role,
            "Status": status,
            "CreatedAt": datetime.strptime(created_at, '%Y-%m-%d') if created_at else current_values['CREATEDAT'],
            "LastLogin": datetime.strptime(last_login, '%Y-%m-%d') if last_login else current_values['LASTLOGIN'],
        }

        differences = [
            key for key, value in updates.items()
            if value is not None and current_values.get(key.upper()) != value
        ]

        if len(differences) > 1:
            return jsonify({"error": "Only one attribute can be updated at a time. Multiple differences found."}), 400

        # Update the record in the Admins table
        if differences:
            attribute_to_update = differences[0]
            value_to_update = updates[attribute_to_update]

            sql_query = f"""
                UPDATE Admins
                SET {attribute_to_update} = ?
                WHERE AdminID = ?
            """
            cursor.execute(sql_query, (value_to_update, admin_id))
            conn.commit()

            return jsonify({"success": f"Attribute {attribute_to_update} successfully updated for Admin ID {admin_id}."}), 200

        return jsonify({"error": "No changes detected in the record."}), 400

    except pyodbc.Error as e:
        return jsonify({"error": f"Database error: {str(e)}"}), 500
    finally:
        cursor.close()

@app.route('/delete_admin', methods=['POST'])
def delete_admin():
    """
    Delete a record from the Admins table based on the provided AdminID.
    """
    data = request.get_json()
    admin_id = data.get('admin_id')

    if not admin_id:
        return jsonify({"error": "Admin ID is required for deletion."}), 400

    cursor = conn.cursor()
    try:
        # Check if the record exists in the Admins table
        cursor.execute("SELECT * FROM Admins WHERE AdminID = ?", (admin_id,))
        admin_record = cursor.fetchone()

        if not admin_record:
            return jsonify({"error": f"No record found for Admin ID: {admin_id}."}), 404

        # Delete the record from the Admins table
        cursor.execute("DELETE FROM Admins WHERE AdminID = ?", (admin_id,))
        conn.commit()

        return jsonify({"success": f"Admin ID: {admin_id} has been successfully deleted."}), 200

    except pyodbc.Error as e:
        conn.rollback()
        return jsonify({"error": f"Database error: {str(e)}"}), 500
    finally:
        cursor.close()

def start_admin_form():
    app.run(port=5005, debug=True)
