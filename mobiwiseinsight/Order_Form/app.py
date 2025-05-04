from flask import Flask, render_template, session, redirect, jsonify, request
import pyodbc
import requests

# API for session-based role retrieval
SESSION_API_URL = "http://127.0.0.1:5003/get_admin_role"

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with a secure key

# Oracle DB connection setup (ODBC)
dsn = 'ODBC_2007'
user = 'arjun_christoph'
password = '2004'
connection = pyodbc.connect(f"DSN={dsn};UID={user};PWD={password}", timeout=10)

# Homepage route to load Order Management Form
@app.route('/')
def discount_form():
    # Retrieve Admin ID from session or API
    admin_id = session.get('admin_id', None)  # Assuming the Admin ID is stored in session
    if admin_id is None:
        return redirect("/")  # Redirect if the admin ID is not found

    return render_template('order_management.html', admin_id=admin_id)

# Role fetching route (if needed by frontend JS)
@app.route('/get_admin_role', methods=['GET'])
def get_admin_role():
    try:
        response = requests.get(SESSION_API_URL)
        if response.status_code == 200:
            role = response.json().get("role")
            admin_id = response.json().get("id")
            session['admin_id'] = admin_id
            return jsonify({"role": role, "admin_id": admin_id}), 200
        else:
            return jsonify({"error": "Unable to fetch admin role."}), 400
    except Exception as e:
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500

# Helper function (optional use)
def get_admin_info():
    response = requests.get(SESSION_API_URL)
    if response.status_code == 200:
        data = response.json()
        return {
            "role": data.get("role"),
            "id": data.get("id")
        }
    return {"role": None, "id": None}

@app.route('/fetch_order_record', methods=['POST'])
def fetch_order_record():
    data = request.get_json()
    order_id = data.get('order_id')

    cursor = connection.cursor()
    try:
        # Check if the Order ID exists in the Orders table
        cursor.execute("SELECT * FROM Orders WHERE OrderID = ?", (order_id,))
        record = cursor.fetchone()

        if record:
            # Get column names from the cursor description
            columns = [column[0] for column in cursor.description]
            response_data = dict(zip(columns, record))

            # Convert date fields to string format if needed
            if response_data.get('OrderDate'):
                response_data['OrderDate'] = response_data['OrderDate'].strftime('%Y-%m-%d')
            if response_data.get('ExpectedDelivery'):
                response_data['ExpectedDelivery'] = response_data['ExpectedDelivery'].strftime('%Y-%m-%d')
            print(response_data)

            return jsonify(response_data), 200
        else:
            return jsonify({"error": f"No record found for Order ID: {order_id}"}), 404

    except pyodbc.Error as e:
        return jsonify({"error": f"Database error: {str(e)}"}), 500
    finally:
        cursor.close()

@app.route('/fetch_next_order', methods=['POST'])
def fetch_next_order():
    """
    Fetch the next order record from the Orders table based on the current OrderID.
    """
    data = request.get_json()
    current_id = data.get('order_id')

    if not current_id:
        return jsonify({"error": "Current Order ID is not provided."}), 400

    cursor = connection.cursor()
    try:
        cursor.execute("""
            SELECT * FROM (
                SELECT * FROM Orders
                WHERE OrderID > ?
                ORDER BY OrderID ASC
            ) WHERE ROWNUM = 1
        """, (current_id,))
        record = cursor.fetchone()

        if record:
            columns = [column[0] for column in cursor.description]
            response_data = dict(zip(columns, record))

            # Format date fields
            if response_data.get('OrderDate'):
                response_data['OrderDate'] = response_data['OrderDate'].strftime('%Y-%m-%d')
            if response_data.get('ExpectedDelivery'):
                response_data['ExpectedDelivery'] = response_data['ExpectedDelivery'].strftime('%Y-%m-%d')

            return jsonify(response_data), 200
        else:
            return jsonify({"error": "No next record found in the Orders table."}), 404

    except pyodbc.Error as e:
        return jsonify({"error": f"Database error: {str(e)}"}), 500
    finally:
        cursor.close()

@app.route('/fetch_previous_order', methods=['POST'])
def fetch_previous_order():
    """
    Fetch the previous order record from the Orders table based on the current OrderID.
    """
    data = request.get_json()
    current_id = data.get('order_id')

    if not current_id:
        return jsonify({"error": "Current Order ID is not provided."}), 400

    cursor = connection.cursor()
    try:
        cursor.execute("""
            SELECT * FROM (
                SELECT * FROM Orders
                WHERE OrderID < ?
                ORDER BY OrderID DESC
            ) WHERE ROWNUM = 1
        """, (current_id,))
        record = cursor.fetchone()

        if record:
            columns = [column[0] for column in cursor.description]
            response_data = dict(zip(columns, record))

            # Format date fields
            if response_data.get('OrderDate'):
                response_data['OrderDate'] = response_data['OrderDate'].strftime('%Y-%m-%d')
            if response_data.get('ExpectedDelivery'):
                response_data['ExpectedDelivery'] = response_data['ExpectedDelivery'].strftime('%Y-%m-%d')

            return jsonify(response_data), 200
        else:
            return jsonify({"error": "No previous record found in the Orders table."}), 404

    except pyodbc.Error as e:
        return jsonify({"error": f"Database error: {str(e)}"}), 500
    finally:
        cursor.close()

@app.route('/update_order', methods=['POST'])
def update_order():
    data = request.get_json()
    order_id = data.get('order_id')
    order_status = data.get('order_status')
    delivery_stage = data.get('delivery_stage')

    if not order_id:
        return jsonify({"error": "Order ID is required."}), 400

    if not order_status or order_status not in ['Active', 'Inactive']:
        return jsonify({"error": "Invalid or missing Order Status."}), 400

    if not delivery_stage or delivery_stage not in ['Pending', 'Dispatched', 'Out for Delivery', 'Delivered']:
        return jsonify({"error": "Invalid or missing Delivery Stage."}), 400

    cursor = connection.cursor()
    try:
        # Check if the order ID exists
        cursor.execute("SELECT * FROM Orders WHERE OrderID = ?", (order_id,))
        existing_order = cursor.fetchone()

        if not existing_order:
            return jsonify({"error": f"Order ID {order_id} does not exist."}), 404

        # Perform update
        cursor.execute("""
            UPDATE Orders
            SET OrderStatus = ?, DeliveryStage = ?
            WHERE OrderID = ?
        """, (order_status, delivery_stage, order_id))

        connection.commit()
        return jsonify({"success": f"Order ID {order_id} has been successfully updated."}), 200

    except pyodbc.Error as e:
        connection.rollback()
        return jsonify({"error": f"Database error: {str(e)}"}), 500

    finally:
        cursor.close()

# Run the app on port 5006
def start_order_management():
    app.run(port=5007, debug=True)
