from flask import Flask, render_template, request, jsonify, redirect, session
import pyodbc
import requests
from datetime import datetime

# API URL for session handler
SESSION_API_URL = "http://127.0.0.1:5003/get_admin_role"

# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with your actual secret key

# Database connection setup
dsn = 'ODBC_2007'
user = 'arjun_christoph'
password = '2004'
connection = pyodbc.connect(f"DSN={dsn};UID={user};PWD={password}", timeout=10)

@app.route('/')
def discount_form():
    # Retrieve Admin ID from session or API
    admin_id = session.get('admin_id', None)  # Assuming the Admin ID is stored in session
    if admin_id is None:
        return redirect("/")  # Redirect if the admin ID is not found

    return render_template('discount_form.html', admin_id=admin_id)

@app.route('/get_next_discount_id', methods=['GET'])
def get_next_discount_id():
    try:
        cursor = connection.cursor()

        # Query to find the next smallest ID (assuming IDs are integers and sequential)
        cursor.execute("""
            SELECT NVL(MAX(DiscountID), 0) + 1 AS next_id
            FROM Mobile_Discounts
        """)
        result = cursor.fetchone()
        next_id = result[0] if result else 1  # Default to 1 if no records exist
        print(f"Next Discount ID: {next_id}")

        cursor.close()
        return jsonify({"next_id": next_id})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/fetch_discount_record', methods=['POST'])
def fetch_discount_record():
    data = request.get_json()
    discount_id = data.get('discount_id')

    cursor = connection.cursor()
    try:
        # Check if the discount ID exists in the Discount table
        cursor.execute("SELECT * FROM Mobile_Discounts WHERE DiscountID = ?", (discount_id,))
        record = cursor.fetchone()

        if record:
            # Get column names from the cursor description
            columns = [column[0] for column in cursor.description]
            response_data = dict(zip(columns, record))

            # Safely convert fields if needed (e.g., discount percentage)
            response_data['DiscountPercentage'] = float(response_data.get('DiscountPercentage', 0))  # Convert to float

            # Return data excluding OldPrice
            response_data.pop('OldPrice', None)

            return jsonify(response_data), 200
        else:
            return jsonify({"error": f"No record found for Discount ID: {discount_id}"}), 404

    except pyodbc.Error as e:
        return jsonify({"error": f"Database error: {str(e)}"}), 500
    finally:
        cursor.close()

@app.route('/fetch_next_discount', methods=['POST'])
def fetch_next_discount():
    """
    Fetch the next discount record from the Mobile_Discounts table based on the current DiscountID.
    """
    data = request.get_json()
    current_id = data.get('discount_id')

    if not current_id:
        return jsonify({"error": "Current Discount ID is not provided."}), 400

    cursor = connection.cursor()
    try:
        # Query for the next discount record
        cursor.execute("""
            SELECT * FROM (
                SELECT * FROM Mobile_Discounts
                WHERE DiscountID > ?
                ORDER BY DiscountID ASC
            ) WHERE ROWNUM = 1
        """, (current_id,))
        record = cursor.fetchone()

        if record:
            # Get column names and prepare response
            columns = [column[0] for column in cursor.description]
            response_data = dict(zip(columns, record))
            response_data['DiscountPercentage'] = float(response_data.get('DiscountPercentage', 0))
            return jsonify(response_data), 200
        else:
            return jsonify({"error": "No next record found in the Mobile Discounts table."}), 404

    except pyodbc.Error as e:
        return jsonify({"error": f"Database error: {str(e)}"}), 500
    finally:
        cursor.close()

@app.route('/fetch_previous_discount', methods=['POST'])
def fetch_previous_discount():
    """
    Fetch the previous discount record from the Mobile_Discounts table based on the current DiscountID.
    """
    data = request.get_json()
    current_id = data.get('discount_id')

    if not current_id:
        return jsonify({"error": "Current Discount ID is not provided."}), 400

    cursor = connection.cursor()
    try:
        # Query for the previous discount record
        cursor.execute("""
            SELECT * FROM (
                SELECT * FROM Mobile_Discounts
                WHERE DiscountID < ?
                ORDER BY DiscountID DESC
            ) WHERE ROWNUM = 1
        """, (current_id,))
        record = cursor.fetchone()

        if record:
            # Get column names and prepare response
            columns = [column[0] for column in cursor.description]
            response_data = dict(zip(columns, record))
            response_data['DiscountPercentage'] = float(response_data.get('DiscountPercentage', 0))
            return jsonify(response_data), 200
        else:
            return jsonify({"error": "No previous record found in the Mobile Discounts table."}), 404

    except pyodbc.Error as e:
        return jsonify({"error": f"Database error: {str(e)}"}), 500
    finally:
        cursor.close()

@app.route('/save_discount', methods=['POST'])
def save_discount():
    """
    Save a record into the Mobile_Discounts table. 
    If the DiscountID already exists, return an error.
    """
    data = request.get_json()

    # Extract form fields
    discount_id = data.get('discount_id')
    offer_name = data.get('offer_name')
    discount_percentage = data.get('discount_percentage')
    start_date = data.get('start_date')
    end_date = data.get('end_date')
    mobile_id = data.get('mobile_id')
    admin_id = data.get('admin_id')

    # Validate required fields
    if not all([discount_id, offer_name, discount_percentage, start_date, end_date, mobile_id, admin_id]):
        return jsonify({"error": "All fields are required."}), 400

    cursor = connection.cursor()
    try:
        # Check if the DiscountID already exists in the Discount table
        cursor.execute("SELECT 1 FROM Mobile_Discounts WHERE DiscountID = ?", (discount_id,))
        if cursor.fetchone():
            return jsonify({"error": f"Discount ID {discount_id} already exists in the Discount table."}), 409
        
        cursor.execute("SELECT Price FROM  Mobiles WHERE MobileID = ?", (mobile_id,))
        if not cursor.fetchone():
            return jsonify({"error": f"Mobile ID {mobile_id} does not exist in the Mobiles table."}), 409
        
        cursor.execute("SELECT Price FROM  Mobiles WHERE MobileID = ?", (mobile_id,))
        price = cursor.fetchone()[0]

        # Insert the new record into the Discount table
        cursor.execute("""
            INSERT INTO Mobile_Discounts (DiscountID, OfferName, DiscountPercentage, StartDate, EndDate, MobileID, AdminID, OldPrice)
            VALUES (?, ?, ?, TO_DATE(?, 'YYYY-MM-DD'), TO_DATE(?, 'YYYY-MM-DD'), ?, ?, ?)
        """, (discount_id, offer_name, discount_percentage, start_date, end_date, mobile_id, admin_id, price))
        connection.commit()

        return jsonify({"success": f"Discount ID {discount_id} successfully saved to the Discount table."}), 200

    except pyodbc.Error as e:
        connection.rollback()
        return jsonify({"error": f"Database error: {str(e)}"}), 500
    finally:
        cursor.close()

@app.route('/update_discount', methods=['POST'])
def update_discount():
    data = request.get_json()
    discount_id = data.get('discount_id')
    offer_name = data.get('offer_name')
    discount_percentage = data.get('discount_percentage')
    start_date = data.get('start_date')
    end_date = data.get('end_date')
    mobile_id = int(data.get('mobile_id'))

    cursor = connection.cursor()
    try:
        # Check if the discount ID exists in the Mobile_Discounts table
        cursor.execute("SELECT * FROM Mobile_Discounts WHERE DiscountID = ?", (discount_id,))
        discount_record = cursor.fetchone()

        if not discount_record:
            return jsonify({"error": f"Discount ID {discount_id} does not exist."}), 404

        # Convert discount record to a dictionary
        column_names = [desc[0] for desc in cursor.description]
        current_values = dict(zip(column_names, discount_record))

        cursor.execute("SELECT Price FROM  Mobiles WHERE MobileID = ?", (mobile_id,))
        if not cursor.fetchone():
            return jsonify({"error": f"Mobile ID {mobile_id} does not exist in the Mobiles table."}), 409
        # Prepare update values
        updates = {
            "OfferName": offer_name,
            "DiscountPercentage": discount_percentage,
            "StartDate": datetime.strptime(start_date, '%Y-%m-%d') if start_date else current_values['STARTDATE'],
            "EndDate": datetime.strptime(end_date, '%Y-%m-%d') if end_date else current_values['ENDDATE'],
            "MobileID": mobile_id,
        }

        updates["DiscountPercentage"] = int(updates["DiscountPercentage"])
        differences = [
            key for key, value in updates.items()
            if value is not None and current_values.get(key.upper()) != value
        ]

        if len(differences) == 0:
            return jsonify({"error": "No changes detected."}), 400
        
        if len(differences) > 1:
            return jsonify({"error": "Only one attribute can be updated at a time. Multiple differences found."}), 400
        
        # Update the record in the buffer table
        if differences:
            attribute_to_update = differences[0]
            value_to_update = updates[attribute_to_update]

            sql_query = f"""
                UPDATE Mobile_Discounts
                SET {attribute_to_update} = ?
                WHERE DiscountID = ?
            """
            cursor.execute(sql_query, (value_to_update, discount_id))
            connection.commit()

        return jsonify({"success": f"Discount ID {discount_id} successfully updated."}), 200

    except pyodbc.Error as e:
        connection.rollback()
        return jsonify({"error": f"Database error: {str(e)}"}), 500
    finally:
        cursor.close()

@app.route('/delete_discount', methods=['POST'])
def delete_discount():
    """
    Delete a discount record from the Mobile_Discounts table based on the provided DiscountID,
    only if the record is not present in the main Mobiles table.
    """
    data = request.get_json()
    discount_id = data.get('discount_id')

    if not discount_id:
        return jsonify({"error": "Discount ID is required for deletion."}), 400

    cursor = connection.cursor()
    try:
        # Check if the record exists in the Mobile_Discounts table
        cursor.execute("SELECT * FROM Mobile_Discounts WHERE DiscountID = ?", (discount_id,))
        discount_record = cursor.fetchone()

        if not discount_record:
            return jsonify({"error": f"No record found in the Mobile Discounts table for Discount ID: {discount_id}."}), 404

        # Delete the record from the Mobile_Discounts table
        cursor.execute("DELETE FROM Mobile_Discounts WHERE DiscountID = ?", (discount_id,))
        connection.commit()

        return jsonify({"success": f"Discount record with Discount ID: {discount_id} has been successfully deleted."}), 200

    except pyodbc.Error as e:
        connection.rollback()
        return jsonify({"error": f"Database error: {str(e)}"}), 500
    finally:
        cursor.close()

@app.route('/get_admin_role', methods=['GET'])
def get_admin_role():
    """
    Fetch the logged-in admin's role and return it as JSON.
    """
    response = requests.get(SESSION_API_URL)
    if response.status_code == 200:
        admin_role = response.json().get("role")
        admin_id = response.json().get("id")  # Get admin ID from the session or API
        session['admin_id'] = admin_id  # Store the admin ID in the session
        print(f"Admin role: {admin_role}, Admin ID: {admin_id}")
        return jsonify({"role": admin_role, "admin_id": admin_id}), 200

def get_user_role():
    """
    Helper function to fetch the user's role and id.
    """
    response = requests.get(SESSION_API_URL)
    if response.status_code == 200:
        data = response.json()
        return {
            "role": data.get("role"),
            "id": data.get("id")
        }
    return {"role": None, "id": None}

def start_discount_form():
    app.run(port=5006, debug=True)
