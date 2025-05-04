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
app.secret_key = 'your_secret_key'  

# Database connection setup
dsn = 'ODBC_2007'  
user = 'arjun_christoph'
password = '2004'
connection = pyodbc.connect(f"DSN={dsn};UID={user};PWD={password}", timeout=10)

@app.route('/')
def mobile_table():
    flash_messages = {category: message for category, message in get_flashed_messages(with_categories=True)}
    return render_template('mobile.html', flash_messages=flash_messages)

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

@app.route('/get_next_mobile_id', methods=['GET'])
def get_next_mobile_id():
    try:
        cursor = connection.cursor()

        # Query to find the next smallest ID (assuming IDs are integers and sequential)
        cursor.execute("""
            SELECT NVL(MAX(MobileID), 0) + 1 AS next_id
            FROM Mobiles_Buffer
        """)
        result = cursor.fetchone()
        next_id = result[0] if result else 1  # Default to 1 if no records exist
        print(f"Next Mobile ID: {next_id}")

        cursor.close()
        return jsonify({"next_id": next_id})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/fetch_mobile_buffer', methods=['POST'])
def fetch_mobile_buffer():
    data = request.get_json()
    mobile_id = data.get('mobile_id')

    cursor = connection.cursor()
    try:
        # Check if the mobile ID exists in the buffer table
        cursor.execute("SELECT * FROM Mobiles_Buffer WHERE MobileID = ?", (mobile_id,))
        record = cursor.fetchone()

        if record:
            # Get column names from the cursor description
            columns = [column[0] for column in cursor.description]
            response_data = dict(zip(columns, record))

            # Debugging: Log the fetched data
            print(f"Record fetched: {record}")
            print(f"Columns fetched: {columns}")

            # Safely convert fields
            response_data['Price'] = float(response_data.get('Price', 0))  # Default to 0 if Price is missing
            response_data['UserRating'] = float(response_data.get('UserRating', 0))  # Convert rating to float

            return jsonify(response_data), 200
        else:
            return jsonify({"error": f"No record found in the buffer table for Mobile ID: {mobile_id}"}), 404

    except pyodbc.Error as e:
        return jsonify({"error": f"Database error: {str(e)}"}), 500
    finally:
        cursor.close()

@app.route('/save_mobile_buffer', methods=['POST'])
def save_mobile_buffer():
    """
    Save a record into the Mobiles_Buffer table. 
    If the MobileID already exists, return an error.
    """
    data = request.get_json()

    # Extract form fields
    mobile_id = data.get('mobile_id')
    model = data.get('model')
    brand = data.get('brand')
    price = data.get('price')
    ram = data.get('ram')
    storage = data.get('storage')
    battery = data.get('battery')
    display = data.get('display')
    processor = data.get('processor')
    front_camera = data.get('front_camera')
    rear_camera = data.get('rear_camera')
    release_date = data.get('release_date')
    user_rating = data.get('user_rating')
    description = data.get('description')
    images = data.get('images')

    if not all([mobile_id, model, brand, price, ram, storage, battery, display, processor, front_camera, rear_camera, release_date, user_rating, description, images]):
        return jsonify({"error": "All fields are required."}), 400

    cursor = connection.cursor()
    try:
        # Check if the MobileID already exists in the buffer table
        cursor.execute("SELECT 1 FROM Mobiles_Buffer WHERE MobileID = ?", (mobile_id,))
        if cursor.fetchone():
            return jsonify({"error": f"Mobile ID {mobile_id} already exists in the buffer table."}), 409

        # Insert the new record into the buffer table
        cursor.execute("""
            INSERT INTO Mobiles_Buffer (MobileID, Model, Brand, Price, RAM, Storage, Battery, Display, Processor, FrontCamera, RearCamera, ReleaseDate, UserRating, Description, Images)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, TO_DATE(?, 'YYYY-MM-DD'), ?, ?, ?)
        """, (mobile_id, model, brand, price, ram, storage, battery, display, processor, front_camera, rear_camera, release_date, user_rating, description, images))
        connection.commit()

        return jsonify({"success": f"Mobile ID {mobile_id} successfully saved to the buffer table."}), 200

    except pyodbc.Error as e:
        connection.rollback()
        return jsonify({"error": f"Database error: {str(e)}"}), 500
    finally:
        cursor.close()

@app.route('/commit_mobile', methods=['POST'])
def commit_mobile():
    data = request.get_json()
    mobile_id = data.get('mobile_id')

    if not mobile_id:
        return jsonify({"error": "Mobile ID is required."})

    cursor = connection.cursor()
    try:
        # Check if Mobile ID exists in the buffer table
        cursor.execute("SELECT * FROM Mobiles_Buffer WHERE MobileID = ?", (mobile_id,))
        buffer_record = cursor.fetchone()
        print(f"Buffer record: {buffer_record}")

        if not buffer_record:
            return jsonify({"error": f"No record found in the buffer table for Mobile ID: {mobile_id}."})

        # Check if Mobile ID exists in the main table
        cursor.execute("SELECT * FROM Mobiles WHERE MobileID = ?", (mobile_id,))
        main_record = cursor.fetchone()

        if main_record:
            # Return an error if the record is already present in the main table
            return jsonify({"error": f"Record with Mobile ID: {mobile_id} already exists in the main table."}), 409

        release_date = buffer_record[11]  # Assuming ReleaseDate is the last column
        if isinstance(release_date, str):
            # Convert to Oracle-compatible format
            release_date = datetime.strptime(release_date, '%Y-%m-%d').strftime('%d-%b-%Y')

        # Insert the record into the main table
        cursor.execute("""
            INSERT INTO Mobiles (MobileID, Model, Brand, Price, RAM, Storage, Battery, Display, Processor, FrontCamera, RearCamera, ReleaseDate, UserRating, Description, Images)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (*buffer_record[:11], release_date, *buffer_record[12:]))  # Replace ReleaseDate with formatted value
        connection.commit()
        return jsonify({"success": f"Record with Mobile ID: {mobile_id} inserted into the main table."})

    except pyodbc.Error as e:
        connection.rollback()
        return jsonify({"error": f"Database error: {str(e)}"})
    finally:
        cursor.close()

@app.route('/fetch_next_mobile_buffer', methods=['POST'])
def fetch_next_mobile_buffer():
    """
    Fetch the next mobile record from the buffer table based on the current MobileID.
    """
    data = request.get_json()
    current_id = data.get('mobile_id')

    if not current_id:
        return jsonify({"error": "Current Mobile ID is not provided."}), 400

    cursor = connection.cursor()
    try:
        # Query for the next record
        cursor.execute("""
            SELECT * FROM (
                SELECT * FROM Mobiles_Buffer
                WHERE MobileID > ?
                ORDER BY MobileID ASC
            ) WHERE ROWNUM = 1
        """, (current_id,))
        record = cursor.fetchone()

        if record:
            # Get column names and prepare response
            columns = [column[0] for column in cursor.description]
            response_data = dict(zip(columns, record))
            response_data['Price'] = float(response_data.get('Price', 0))
            response_data['UserRating'] = float(response_data.get('UserRating', 0))  # Convert rating to float
            return jsonify(response_data), 200
        else:
            return jsonify({"error": "No next record found in the buffer table."}), 404

    except pyodbc.Error as e:
        return jsonify({"error": f"Database error: {str(e)}"}), 500
    finally:
        cursor.close()

@app.route('/fetch_previous_mobile_buffer', methods=['POST'])
def fetch_previous_mobile_buffer():
    """
    Fetch the previous mobile record from the buffer table based on the current MobileID.
    """
    data = request.get_json()
    current_id = data.get('mobile_id')

    if not current_id:
        return jsonify({"error": "Current Mobile ID is not provided."}), 400

    cursor = connection.cursor()
    try:
        # Query for the previous record
        cursor.execute("""
            SELECT * FROM (
                SELECT * FROM Mobiles_Buffer
                WHERE MobileID < ?
                ORDER BY MobileID DESC
            ) WHERE ROWNUM = 1
        """, (current_id,))
        record = cursor.fetchone()

        if record:
            # Get column names and prepare response
            columns = [column[0] for column in cursor.description]
            response_data = dict(zip(columns, record))
            response_data['Price'] = float(response_data.get('Price', 0))
            response_data['UserRating'] = float(response_data.get('UserRating', 0))  # Convert rating to float
            return jsonify(response_data), 200
        else:
            return jsonify({"error": "No previous record found in the buffer table."}), 404

    except pyodbc.Error as e:
        return jsonify({"error": f"Database error: {str(e)}"}), 500
    finally:
        cursor.close()

@app.route('/update_mobile_buffer', methods=['POST'])
def update_mobile_buffer():
    data = request.get_json()
    mobile_id = data.get('mobile_id')
    model = data.get('model')
    brand = data.get('brand')
    price = data.get('price')
    ram = data.get('ram')
    storage = data.get('storage')
    battery = data.get('battery')
    display = data.get('display')
    processor = data.get('processor')
    front_camera = data.get('front_camera')
    rear_camera = data.get('rear_camera')
    release_date = data.get('release_date')
    user_rating = data.get('user_rating')
    description = data.get('description')
    images = data.get('images')

    cursor = connection.cursor()
    try:
        # Check if the mobile ID exists in the buffer table
        cursor.execute("SELECT * FROM Mobiles_Buffer WHERE MobileID = ?", (mobile_id,))
        buffer_record = cursor.fetchone()

        if not buffer_record:
            return jsonify({"error": f"Mobile ID {mobile_id} does not exist in the buffer table."}), 404

        # Convert buffer record to a dictionary
        column_names = [desc[0] for desc in cursor.description]
        current_values = dict(zip(column_names, buffer_record))

        # Check if the mobile ID exists in the main table
        cursor.execute("SELECT * FROM Mobiles WHERE MobileID = ?", (mobile_id,))
        main_record = cursor.fetchone()

        if main_record:
            return jsonify({"error": f"Record with Mobile ID {mobile_id} exists in the main table and cannot be updated in the buffer."}), 409

        # Compare received data with the buffer record
        updates = {
            "Model": model,
            "Brand": brand,
            "Price": price,
            "RAM": ram,
            "Storage": storage,
            "Battery": battery,
            "Display": display,
            "Processor": processor,
            "FrontCamera": front_camera,
            "RearCamera": rear_camera,
            "ReleaseDate": datetime.strptime(release_date, '%Y-%m-%d') if release_date else current_values['RELEASEDATE'],
            "UserRating": user_rating,
            "Description": description,
            "Images" : images,
        }

        updates["Price"] = Decimal(updates["Price"]) if updates["Price"] else None
        updates["UserRating"] = Decimal(updates["UserRating"]) if updates["UserRating"] else None

        differences = [
            key for key, value in updates.items()
            if value is not None and current_values.get(key.upper()) != value
        ]

        if len(differences) > 2:
            return jsonify({"error": "Only one attribute can be updated at a time. Multiple differences found."}), 400

        # Update the record in the buffer table
        if differences:
            attribute_to_update = differences[0]
            value_to_update = updates[attribute_to_update]

            sql_query = f"""
                UPDATE Mobiles_Buffer
                SET {attribute_to_update} = ?
                WHERE MobileID = ?
            """
            cursor.execute(sql_query, (value_to_update, mobile_id))
            connection.commit()

            return jsonify({"success": f"Attribute {attribute_to_update} successfully updated for Mobile ID {mobile_id}."}), 200

        return jsonify({"error": "No changes detected in the record."}), 400

    except pyodbc.Error as e:
        return jsonify({"error": f"Database error: {str(e)}"}), 500
    finally:
        cursor.close()

@app.route('/delete_mobile_buffer', methods=['POST'])
def delete_mobile_buffer():
    """
    Delete a record from the Mobiles_Buffer table based on the provided MobileID,
    only if the record is not present in the main Mobiles table.
    """
    data = request.get_json()
    mobile_id = data.get('mobile_id')

    if not mobile_id:
        return jsonify({"error": "Mobile ID is required for deletion."}), 400

    cursor = connection.cursor()
    try:
        # Check if the record exists in the buffer table
        cursor.execute("SELECT * FROM Mobiles_Buffer WHERE MobileID = ?", (mobile_id,))
        buffer_record = cursor.fetchone()

        if not buffer_record:
            return jsonify({"error": f"No record found in the buffer table for Mobile ID: {mobile_id}."}), 404

        # Check if the record exists in the main Mobiles table
        cursor.execute("SELECT * FROM Mobiles WHERE MobileID = ?", (mobile_id,))
        main_record = cursor.fetchone()

        if main_record:
            return jsonify({"error": f"Record with Mobile ID: {mobile_id} exists in the main table and cannot be deleted from the buffer."}), 409

        # Delete the record from the buffer table
        cursor.execute("DELETE FROM Mobiles_Buffer WHERE MobileID = ?", (mobile_id,))
        connection.commit()

        return jsonify({"success": f"Record with Mobile ID: {mobile_id} has been successfully deleted."}), 200

    except pyodbc.Error as e:
        connection.rollback()
        return jsonify({"error": f"Database error: {str(e)}"}), 500
    finally:
        cursor.close()

@app.route('/admin_login')
def admin_login():
    return redirect("http://127.0.0.1:5000")  # Redirect to mobile.html

def start_mobile():
    app.run(port=5004, debug=True)