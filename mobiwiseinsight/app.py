import requests
from flask import Flask, render_template, request, jsonify, make_response, redirect, send_from_directory
from datetime import datetime, timedelta, date
import random
import pyodbc
import subprocess
import os
import sys
import json
import re
from functools import wraps
import jwt
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR
from threading import Thread
import uuid
from flask_compress import Compress
from flask_caching import Cache
import logging

# Ensure the 'programs' folder is in the Python module path
sys.path.append(os.path.join(os.path.dirname(__file__), "programs"))

# Now you can import compare.py
from compare import compare_and_recommend
from whatsapp_msg import send_whatsapp_message, send_order_confirmation_whatsapp
from ai_ad import generate_all_discount_ads
from chatbot import get_chatbot_reply
from email_msg import send_email

app = Flask(__name__)
Compress(app)

SECRET_KEY = "your_super_secret_key"  # Keep this secure

cache = Cache(app, config={'CACHE_TYPE': 'simple'})

# Configure file handler only (disable terminal output)
file_handler = logging.FileHandler("request_logs.log")
file_handler.setLevel(logging.INFO)

# Optional: Custom format for log entries
formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s')
file_handler.setFormatter(formatter)

# Clear previous handlers and add only file handler
app.logger.handlers = []
app.logger.addHandler(file_handler)
app.logger.setLevel(logging.INFO)

# Database connection setup
dsn = '****MASKED****'  
user = '****MASKED****'
password = '****MASKED****'
conn = pyodbc.connect(f"DSN={dsn};UID={user};PWD={password}", timeout=10)

user = None
discounted_mobiles = []
comparison_links = {}  # Temporary in-memory storage

# Decode token
def decode_token(token):
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

# Auth check decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.cookies.get("jwt")
        if not token:
            return redirect("/")  # Or your login page
        user = decode_token(token)
        if not user:
            return redirect("/")
        return f(*args, **kwargs, user=user)
    return decorated_function

def clean_gemini_output(text):
    # Remove code blocks if present
    text = re.sub(r"```json|```", "", text).strip()
    
    # Optionally fix smart quotes if present
    text = text.replace("“", "\"").replace("”", "\"").replace("’", "'")

    text = text.replace("*", "")  # Remove asterisks if present

    return text

# Function to format number in Indian style (lakhs, crores)
def indian_format(number):
    number = int(number)  # Remove decimal part (paise)
    num_str = str(number)[::-1]  # Reverse the string for easy grouping

    # Group first three digits, then every two digits
    parts = [num_str[:3]] + [num_str[i:i + 2] for i in range(3, len(num_str), 2)]

    # Join the parts and reverse back to original order
    return ','.join(parts)[::-1]

def generate_discount_ads_async(discount_data):
    global discounted_mobiles
    try:
        discounted_mobiles = generate_all_discount_ads(discount_data)
        print("✅ Discount ads generated in background.")
    except Exception as e:
        print("❌ Error in ad generation:", e)

def to_date(obj):
    if isinstance(obj, str):
        try:
            return datetime.strptime(obj, "%Y-%m-%d").date()
        except ValueError:
            return datetime.strptime(obj, "%Y-%m-%d %H:%M:%S").date()
    elif isinstance(obj, datetime):
        return obj.date()
    elif isinstance(obj, date):
        return obj  # Already a date
    return None  # Unexpected type

@app.before_request
def log_request_info():
    username = "Guest"
    token = request.cookies.get("jwt")
    if token:
        user_data = decode_token(token)
        if user_data and "username" in user_data:
            username = user_data["username"]

    app.logger.info(f"{request.method} {request.path} | User: {username}")

@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-store'
    return response

@app.route('/')
def homepage():
    try:
        news_articles = fetch_mobile_news()
        cursor = conn.cursor()
        cursor.execute("""
                SELECT MobileID, Model, TO_CHAR(Price, '99,99,999'), Images 
                FROM (
                    SELECT MobileID, Model, Price, Images 
                    FROM Mobiles 
                    ORDER BY DBMS_RANDOM.VALUE
                ) WHERE ROWNUM <= 20
        """)
        mobiles = [{"id": row[0], "model": row[1], "price": row[2], "image": row[3]} for row in cursor.fetchall()]
        cursor.execute("""
            SELECT m.MobileID, m.Model, m.Images, d.OfferName, d.DiscountPercentage, 
                   TO_CHAR(m.Price, '99,99,999')
            FROM Mobiles m
            JOIN Mobile_Discounts d ON m.MobileID = d.MobileID
            WHERE d.Status = 'Active'
        """)
        discount_data = cursor.fetchall()
        discount_data = random.sample(discount_data, min(5, len(discount_data)))
        cursor.close()
        
        # Start image generation in a separate thread
        ad_thread = Thread(target=lambda: generate_discount_ads_async(discount_data))
        ad_thread.start()

        # Wait for ad generation to complete (max 25 seconds)
        ad_thread.join(timeout=25)
        # Fallback if ads are missing
        if len(discounted_mobiles) < 5:
            static_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), "static", "discount_images"))
            if not os.path.exists(static_folder):
                print("⚠️ Static folder not found for fallback images.")
            try:
                fallback_files = [f for f in os.listdir(static_folder) if f.endswith(".jpg")]
                random.shuffle(fallback_files)
                for file in fallback_files[:5 - len(discounted_mobiles)]:
                    mobile_id = file.split(".")[0]
                    discounted_mobiles.append({
                        "id": mobile_id,
                        "model": f"Model {mobile_id}",
                        "image_path": f"/static/discount_images/{file}",
                        "offer": "Special Deal",
                        "discount": "10%",
                        "price": "Unavailable"
                    })
            except Exception as e:
                print("⚠️ Error using fallback images:", e)
        token = request.cookies.get("jwt")
        if token:
            global user
            user = decode_token(token)  
        return render_template('home.html', user=user, news=news_articles[:3], mobiles=mobiles, discounted_mobiles=discounted_mobiles)  # Pass 3 news articles
    
    except pyodbc.Error as e:
        print(f"Database error: {e}")
        return "Database connection error, please check logs."

displayed_articles = set()  # Store already displayed articles to prevent duplicates

@app.route("/logout")
def logout():
    global user
    user = None
    response = make_response(redirect("/"))
    response.delete_cookie("jwt")
    return response

def fetch_mobile_news():
    sources = [
        "https://newsapi.org/v2/everything?q=smartphone%20OR%20%22mobile%20phone%22%20OR%20%22mobile%20technology%22&language=en&sortBy=publishedAt&apiKey=****MASKED****",
        "https://gnews.io/api/v4/search?q=smartphone%20OR%20%22mobile%20device%22&lang=en&sortby=publishedAt&token=****MASKED****",
        "https://api.currentsapi.services/v1/latest-news?keywords=smartphone%20technology&language=en&apiKey=****MASKED****",
        "https://real-time-amazon-data.p.rapidapi.com/product-details",
        "https://api.thenewsapi.com/v1/news/all?api_token=****MASKED****&search=smartphones&language=en&limit=10",
        #"https://contextualwebsearch-websearch-v1.p.rapidapi.com/api/search/NewsSearchAPI?q=smartphone&pageNumber=1&pageSize=10&autoCorrect=true",
        "http://api.mediastack.com/v1/news?access_key=****MASKED****&keywords=smartphone&languages=en",
        #"https://content.guardianapis.com/search?q=smartphone&api-key=****MASKED****"
    ]

    headers = {
        "X-RapidAPI-Host": "real-time-amazon-data.p.rapidapi.com",
        "X-RapidAPI-Key": "****MASKED****"
    }

    querystring = {"asin":"B07ZPKBL9V","country":"US"}

    news_articles = []

    for url in sources:
        try:
            response = requests.get(url, headers=headers if "rapidapi" in url else None, params=querystring if "rapidapi" in url else None)
            
            if response.status_code == 200:
                    data = response.json()
                    articles = data.get("articles", data.get("news", []))  
                    
                    for article in articles:
                        if article.get("urlToImage") or article.get("image") or article.get("image_url"):  # Ensure only articles with images
                            news_articles.append({
                                "title": article.get("title", "No Title"),
                                "description": article.get("description", "No description available")[:150] + "...",
                                "image": article.get("urlToImage") if article.get("urlToImage") else (article.get("image") if article.get("image") else article.get("image_url")),
                                "url": article.get("url", "#"),
                                "publishedAt": article.get("publishedAt", "Unknown Date")[:10]
                            })

        except Exception as e:
            print(f"Error fetching news from {url}: {e}")  # Debugging if an API fails

    if not news_articles:
        return [{"title": "No news available", "description": "Try again later.", "image": "/static/images/no-news.png", "url": "#", "publishedAt": "N/A"}]
    
    random.shuffle(news_articles)  # Shuffle news to prevent repetition
    return news_articles[:21]  # Return latest 20 articles

@app.route('/latest-news')
def latest_news():
    news_articles = fetch_mobile_news()
    return render_template('latest_news.html',user=user, news=news_articles)

@cache.cached(timeout=1800)
@app.route('/latest-news/page')
def latest_news_page():
    news_articles = fetch_mobile_news()
    return jsonify(news_articles)

@app.route('/mobile-details/<string:mobile_id>')
def mobile_details(mobile_id):
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT MobileID, Model, Brand, TO_CHAR(Price, '99,99,999') AS Price, RAM, Storage, Battery, Display, Processor, FrontCamera, RearCamera, ReleaseDate, UserRating, Description, Images FROM Mobiles WHERE MobileID = ?", (mobile_id,))
        mobile = cursor.fetchone()

        if not mobile:
            return "Mobile not found", 404

        columns = [desc[0] for desc in cursor.description]
        mobile_data = dict(zip(columns, mobile))  # Assuming ReleaseDate is the last column

        # Ensure release date is formatted as YYYY-MM-DD (without time)
        if "RELEASEDATE" in mobile_data and mobile_data["RELEASEDATE"]:
            mobile_data["RELEASEDATE"] = mobile_data["RELEASEDATE"].strftime("%Y-%m-%d")


        return render_template('mobile_details.html', mobile=mobile_data, user=user)

    except Exception as e:
        return f"Error: {str(e)}", 500

    finally:
        cursor.close()

@app.route('/all-mobiles')
def all_mobiles():
    """Fetch all mobiles, shuffle them, and loop after the last mobile"""
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT MobileID, Model, Brand, TO_CHAR(Price, '99,99,999') AS Price, RAM, Storage, Battery, 
                   Display, Processor, FrontCamera, RearCamera, TO_CHAR(ReleaseDate, 'YYYY-MM-DD') AS ReleaseDate, 
                   UserRating, Description, Images 
            FROM Mobiles
        """)
        
        mobiles = cursor.fetchall()

        # Convert database records to dictionary
        column_names = [desc[0] for desc in cursor.description]
        mobiles_list = [dict(zip(column_names, row)) for row in mobiles]

        # Shuffle the mobile list
        random.shuffle(mobiles_list)

        return render_template('all_mobiles.html', mobiles=mobiles_list, user=user)

    except pyodbc.Error as e:
        return jsonify({"error": f"Database error: {str(e)}"}), 500
    finally:
        cursor.close()

@app.route('/filter-mobiles', methods=['POST'])
def filter_mobiles():
    data = request.get_json()
    brand = data.get('brand', '')
    price = data.get('price', '')
    ram = data.get('ram', '')
    storage = data.get('storage', '')

    query = """
        SELECT MobileID, Model, Brand, TO_CHAR(Price, '99,99,999') AS Price, RAM, Storage, Battery, Display, Processor, 
               FrontCamera, RearCamera, ReleaseDate, UserRating, Description, Images
        FROM Mobiles
    """
    
    params = []

    if brand or price or ram or storage:
        query += " WHERE"

    if brand:
        query += " Brand = ?"
        params.append(brand)

    if brand and price:
        query += " AND"
    
    if price:
        query += " Price <= ?"
        params.append(price)

    if (brand or price) and ram:
        query += " AND"

    if ram:
        query += " RAM = ?"
        params.append(ram)

    if (brand or price or ram) and storage:
        query += " AND"

    if storage:
        query += " Storage = ?"
        params.append(storage)

    cursor = conn.cursor()
    try:
        cursor.execute(query, params)
        mobiles = cursor.fetchall()

        # Convert database records to dictionary
        column_names = [desc[0] for desc in cursor.description]
        mobiles_list = [dict(zip(column_names, row)) for row in mobiles]

        # Shuffle the mobile list for randomness
        random.shuffle(mobiles_list)
        print(mobiles_list)

        return jsonify({"mobiles": mobiles_list})

    except pyodbc.Error as e:
        return jsonify({"error": f"Database error: {str(e)}"}), 500
    finally:
        cursor.close()

@app.route('/search-mobiles', methods=['POST'])
def search_mobiles():
    data = request.get_json()
    search_query = data.get('query', '').strip()

    if not search_query:
        return jsonify({"mobiles": []})  # Return empty if no input

    query = """
        SELECT MobileID, Model, Brand, TO_CHAR(Price, '99,99,999') AS Price, Images
        FROM Mobiles
        WHERE LOWER(Model) LIKE LOWER(?) OR LOWER(Brand) LIKE LOWER(?)
    """
    params = [f"%{search_query}%", f"%{search_query}%"]

    cursor = conn.cursor()
    try:
        cursor.execute(query, params)
        mobiles = cursor.fetchall()

        column_names = [desc[0] for desc in cursor.description]
        mobiles_list = [dict(zip(column_names, row)) for row in mobiles]

        return jsonify({"mobiles": mobiles_list})

    except pyodbc.Error as e:
        return jsonify({"error": f"Database error: {str(e)}"}), 500
    finally:
        cursor.close()

@app.route('/compare-mobiles')
def compare_mobiles_page():
    return render_template('compare_mobiles.html', user=user)

@app.route('/compare-mobiles', methods=['POST'])
def compare_mobiles():
    data = request.get_json()
    mobile_ids = data.get('mobile_ids', [])
    preferences = data.get('preferences', [])

    if len(mobile_ids) < 2:
        return jsonify({"error": "Select at least two mobiles to compare"}), 400

    cursor = conn.cursor()
    placeholders = ', '.join('?' for _ in mobile_ids)

    cursor.execute("""ALTER SESSION SET NLS_TERRITORY = 'INDIA'""")

    cursor.execute(f"""
        SELECT MobileID, Model, Brand, TO_CHAR(Price, '99,99,999') AS Price, RAM, Storage, Battery, Display, Processor, 
               FrontCamera, RearCamera, UserRating, Images
        FROM Mobiles WHERE MobileID IN ({placeholders})
    """, mobile_ids)

    mobiles_data = cursor.fetchall()
    cursor.close()

    column_names = ["MobileID", "Model", "Brand", "Price", "RAM", "Storage", "Battery",
                    "Display", "Processor", "FrontCamera", "RearCamera", "UserRating", "Images"]
    mobiles_list = [dict(zip(column_names, row)) for row in mobiles_data]

    # Get AI-based comparison and suggestion
    ai_output_raw = compare_and_recommend(mobiles_list, preferences)


    try:
        clean_output = clean_gemini_output(ai_output_raw)
        ai_results = json.loads(clean_output)

    except Exception as e:
        print("Error parsing AI output:", e)
        ai_results = {
            "comparisons": [],
            "best_suggestion": {
                "model": "N/A",
                "brand": "N/A",
                "price": "N/A",
                "reason": "AI parsing failed. Please try again."
            }
        }

    # print("AI Comparison & Recommendation: ", ai_results)

    # Return both AI output and mobile specs
    return jsonify({
        "mobiles": mobiles_list,
        "comparisons": ai_results.get("comparisons", []),
        "best_suggestion": ai_results.get("best_suggestion", {})
    })

@app.route('/add-to-cart', methods=['POST'])
def add_to_cart():
    try:
        data = request.get_json()
        mobile_id = data.get("mobile_id")
        
        if not user:
            return jsonify({"success": False, "message": "Login/Sign Up required"})
        
        # Get user ID from username
        cursor = conn.cursor()
        cursor.execute("SELECT UserID FROM Users WHERE Username = ?", (user["username"],))
        result = cursor.fetchone()
        
        if not result:
            return jsonify({"success": False, "message": "User not found"})
        user_id = int(result[0])

        # Insert into Cart table using sequence
        cursor.execute("INSERT INTO Cart (CartID, UserID, MobileID) VALUES (cart_seq.NEXTVAL, ?, ?)", (user_id, mobile_id))
        conn.commit()
        cursor.close()

        return jsonify({"success": True})

    except Exception as e:
        print("Error in add_to_cart:", e)
        return jsonify({"success": False, "message": "Error adding to cart"})
    
@app.route('/cart')
def cart():
    if not user:
        return render_template('cart.html', total_items=0, grand_total=0, user=None, cart_items={})
    cursor = conn.cursor()
    try:
        # Get user ID from the logged-in user
        cursor.execute("SELECT UserID FROM Users WHERE Username = ?", (user["username"],))
        result = cursor.fetchone()
        user_id = result[0]

        # Fetch cart items for the logged-in user
        cursor.execute("""
            SELECT m.MobileID, m.Model, TO_CHAR(m.Price, '99,99,999') AS Price, m.Images, m.Brand
            FROM Cart c
            JOIN Mobiles m ON c.MobileID = m.MobileID
            WHERE c.UserID = ?
        """, (user_id,))
        
        cart_items = cursor.fetchall()
        total_items = len(cart_items)
        grand_total = sum([float(item[2].replace(",", "")) for item in cart_items])
        grand_total = indian_format(grand_total)

        # Return the cart items as JSON
        cart_data = [{
            "mobile_id": item[0],
            "model": item[1],
            "brand": item[4],
            "price": item[2],
            "image": item[3]
        } for item in cart_items]

        return render_template('cart.html', total_items=total_items, grand_total=grand_total, user=user, cart_items=cart_data)
    
    except pyodbc.Error as e:
        return jsonify({"success": False, "message": "Database error"}), 500
    finally:
        cursor.close()

@app.route('/remove-from-cart', methods=['POST'])
def remove_from_cart():
    try:
        data = request.get_json()
        mobile_id = data.get("mobile_id")

        # Get user ID from the logged-in user
        cursor = conn.cursor()
        cursor.execute("SELECT UserID FROM Users WHERE Username = ?", (user["username"],))
        result = cursor.fetchone()
        user_id = result[0]

        # Remove item from the cart
        cursor.execute("DELETE FROM Cart WHERE UserID = ? AND MobileID = ?", (user_id, mobile_id))
        conn.commit()

        return jsonify({"success": True, "message": "Item removed from cart!"})

    except pyodbc.Error as e:
        return jsonify({"success": False, "message": "Error removing from cart"}), 500
    finally:
        cursor.close()

@app.route('/checkout', methods=['POST'])
def checkout():
    try:
        data = request.get_json()
        
        address = data.get("address", {})
        payment_method = data.get("payment_method", "Cash on Delivery")
        order_status = data.get("order_status", "Active")
        delivery_stage = data.get("delivery_stage", "Dispatched")
        mobile_ids = data.get("mobile_ids", [])

        if not user:
            return jsonify({"success": False, "message": "Login required"}), 401

        cursor = conn.cursor()

        # Get user ID
        cursor.execute("SELECT UserID FROM Users WHERE Username = ?", (user["username"],))
        user_id = cursor.fetchone()[0]

        # Insert new address
        cursor.execute("""
            INSERT INTO UserAddresses (AddressID, UserID, DoorStreet, Locality, City, Country, Pincode)
            VALUES (address_seq.NEXTVAL, ?, ?, ?, ?, ?, ?)
        """, (user_id, address["door_street"], address["locality"], address["city"], address["country"], address["pincode"]))

        # Get AddressID from CURRVAL
        cursor.execute("SELECT address_seq.CURRVAL FROM dual")
        address_id = cursor.fetchone()[0]

        # Expected delivery date (within 7 days)
        expected_delivery = datetime.now().date() + timedelta(days=random.randint(0, 6))

        # Insert order for each mobile
        for mobile_id in mobile_ids:
            cursor.execute("""
                INSERT INTO Orders (OrderID, UserID, AddressID, MobileID, PaymentMethod, ExpectedDelivery, OrderDate)
                VALUES (order_seq.NEXTVAL, ?, ?, ?, ?, TO_DATE(?, 'YYYY-MM-DD'), SYSDATE)
            """, (user_id, address_id, mobile_id, payment_method, expected_delivery.strftime('%Y-%m-%d')))

        conn.commit()

                # Fetch phone number and username
        cursor.execute("SELECT Phone, Username FROM Users WHERE UserID = ?", (user_id,))
        result = cursor.fetchone()
        phone_number = result[0]
        username = result[1]

        # Calculate grand total
        cursor.execute("SELECT Price FROM Mobiles WHERE MobileID IN ({})".format(','.join(['?']*len(mobile_ids))), mobile_ids)
        prices = cursor.fetchall()
        grand_total = sum([float(price[0]) for price in prices])
        grand_total = indian_format(grand_total)

        # Send email confirmation
        subject = "Order Confirmation - MobiWise Insight"
        body = f"""
        Hello {username},

        ✅ Your order has been placed successfully on MobiWise Insight.

        📱 Number of Mobiles: {len(mobile_ids)}
        💰 Grand Total: ₹{grand_total}
        📦 Expected Delivery Date: {expected_delivery.strftime('%d-%m-%Y')}

        Thank you for shopping with us!
        """

        # Fetch user email
        cursor.execute("SELECT Email FROM Users WHERE UserID = ?", (user_id,))
        email = cursor.fetchone()[0]

        if send_email(email, subject, body):
            print(f"✅ Order confirmation email sent to {email}")
        else:
            print(f"❌ Failed to send email to {email}")

        # Send WhatsApp order confirmation
        send_order_confirmation_whatsapp(phone_number, username, expected_delivery, len(mobile_ids), grand_total)

        cursor.close()

        return jsonify({"success": True, "message": "Order placed successfully!"})

    except Exception as e:
        print("Checkout error:", e)
        return jsonify({"success": False, "message": "An error occurred during checkout"}), 500

# Function to check cart and send WhatsApp messages for applicable discounts
def check_cart_and_send_discount_notifications():
    cursor = conn.cursor()
    today = datetime.now().date()

    # First, fetch the OldPrice for matching records
    cursor.execute("""
        SELECT MobileID, OldPrice
        FROM Mobile_Discounts
        WHERE EndDate = ? AND Status = 'Active'
    """, (today,))

    rows = cursor.fetchall()

    # Second, update the Mobiles table using the fetched values
    for mobile_id, old_price in rows:
        cursor.execute("""
            UPDATE Mobiles
            SET Price = ?
            WHERE MobileID = ?
        """, (old_price, mobile_id))

    cursor.execute("""
        UPDATE Mobile_Discounts
        SET Status = 'Inactive'
        WHERE EndDate = ? AND Status = 'Active'
    """, (today,))
    conn.commit()


    # Step 2: Fetch all cart items with active discounts
    cursor.execute("""
        SELECT c.UserID, c.MobileID, u.Phone, m.Model, m.Price, m.Images,
        d.DiscountPercentage, TO_CHAR(d.StartDate, 'YYYY-MM-DD') AS StartDate, TO_CHAR(d.EndDate, 'YYYY-MM-DD') AS EndDate
        FROM Cart c
        JOIN Mobiles m ON c.MobileID = m.MobileID
        JOIN Users u ON c.UserID = u.UserID
        JOIN Mobile_Discounts d ON c.MobileID = d.MobileID
        WHERE d.Status = 'Active'
    """)

    cart_items = cursor.fetchall()

    for item in cart_items:
        user_id, mobile_id, phone, model, price, image, discount_pct, start_date, end_date = item
        send_today = None
        notification_type = None

        start_date = to_date(start_date)
        end_date = to_date(end_date)

        # Case 1: 7th day since discount started
        if (today - start_date).days == 7:
            send_today = True
            notification_type = '7th_day'
        # Case 2: Last day of discount
        elif end_date == today:
            send_today = True
            notification_type = 'last_day'
        # Case 3: First day
        elif start_date == today:
            send_today = True
            notification_type = 'first_day'        

        if send_today:

            # Check if already sent today
            cursor.execute("""
                SELECT COUNT(*) FROM Discount_Notifications
                WHERE UserID = ? AND MobileID = ? AND NotificationDate = ? AND Type = ?
            """, (user_id, mobile_id, today, notification_type))

            already_sent = cursor.fetchone()[0]

            if already_sent == 0:
                try:
                    send_whatsapp_message(phone, model, discount_pct, price, mobile_id)
                    print(f"✅ WhatsApp message sent to {phone} for {model} ({notification_type})")

                    # Log the notification
                    cursor.execute("""
                        INSERT INTO Discount_Notifications (UserID, MobileID, NotificationDate, Type)
                        VALUES (?, ?, ?, ?)
                    """, (user_id, mobile_id, today, notification_type))
                    conn.commit()
                except Exception as e:
                    print(f"❌ Error sending WhatsApp or logging notification: {e}")

    cursor.close()

@app.route('/generate-compare-link', methods=['POST'])
def generate_compare_link():
    data = request.get_json()
    mobile_ids = data.get("mobile_ids", [])
    preferences = data.get("preferences", [])
    
    if not mobile_ids:
        return jsonify({"error": "No mobiles selected"}), 400

    token = request.cookies.get("jwt")
    user_data = decode_token(token) if token else {}

    # Generate a unique key
    link_id = str(uuid.uuid4())

    # Save the session data in-memory
    comparison_links[link_id] = {
        "mobile_ids": mobile_ids,
        "preferences": preferences,
        "user": user_data
    }

    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO Shared_Comparisons (LinkID, MobileID1, MobileID2, MobileID3, MobileID4, Username)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            link_id,
            mobile_ids[0] if len(mobile_ids) > 0 else None,
            mobile_ids[1] if len(mobile_ids) > 1 else None,
            mobile_ids[2] if len(mobile_ids) > 2 else None,
            mobile_ids[3] if len(mobile_ids) > 3 else None,
            user_data.get("username", None)  # Save username if available
        ))
        conn.commit()
        cursor.close()
    except Exception as e:
        print("DB Error saving shared comparison:", e)
        return jsonify({"error": "Could not save link"}), 500

    full_link = request.host_url.rstrip('/') + "/shared-compare/" + link_id
    return jsonify({"link": full_link})

@app.route('/shared-compare/<string:link_id>')
def shared_compare_view(link_id):
    data = comparison_links.get(link_id)

    if not data:
        return "Link expired or invalid", 404

    return render_template("shared_comparison.html",
                           mobile_ids=data["mobile_ids"],
                           preferences=data["preferences"],
                           user=data.get("user", {}))

@app.route('/chatbot', methods=['POST'])
def chatbot_reply():
    data = request.get_json()
    user_msg = data.get("message", "").strip()

    if not user_msg:
        return jsonify({"reply": "Please type something!"})

    try:
        # Get user ID from JWT
        token = request.cookies.get("jwt")
        user_data = decode_token(token) if token else None

        if not user_data:
            return jsonify({"reply": "Please log in to continue."})

        cursor = conn.cursor()
        cursor.execute("SELECT UserID FROM Users WHERE Username = ?", (user_data["username"],))
        user_id = cursor.fetchone()[0]

        # Check or create today's session
        cursor.execute("""
            SELECT SessionID FROM ChatSessions
            WHERE UserID = ? AND TRUNC(StartTime) = TRUNC(SYSDATE)
        """, (user_id,))
        row = cursor.fetchone()

        if row:
            session_id = row[0]
        else:
            cursor.execute("INSERT INTO ChatSessions (SessionID, UserID) VALUES (chat_sessions_seq.NEXTVAL, ?)", (user_id,))
            cursor.execute("SELECT chat_sessions_seq.CURRVAL FROM dual")
            session_id = cursor.fetchone()[0]

        # Save user message
        cursor.execute("""
            INSERT INTO ChatMessages (MessageID, SessionID, Sender, MessageText)
            VALUES (chat_messages_seq.NEXTVAL, ?, 'user', ?)
        """, (session_id, user_msg))

        # Get AI response
        response = get_chatbot_reply(user_msg)
        bot_reply = clean_gemini_output(response)

        # Save bot message
        cursor.execute("""
            INSERT INTO ChatMessages (MessageID, SessionID, Sender, MessageText)
            VALUES (chat_messages_seq.NEXTVAL, ?, 'bot', ?)
        """, (session_id, bot_reply))

        conn.commit()
        cursor.close()

        return jsonify({"reply": bot_reply})

    except Exception as e:
        print("Chatbot Error:", e)
        return jsonify({"reply": "Sorry, something went wrong."})

@app.route('/dino-game/<path:filename>')
def dino_game_files(filename):
    return send_from_directory('Dino_Game', filename)

@app.route('/order-details')
def order_details():
    token = request.cookies.get("jwt")
    user_data = decode_token(token) if token else None

    if not user_data:
        return render_template("track_order.html", user=None, orders=[])

    cursor = conn.cursor()
    try:
        cursor.execute("SELECT UserID FROM Users WHERE Username = ?", (user_data["username"],))
        user_id = cursor.fetchone()[0]

        cursor.execute("""
            SELECT o.ExpectedDelivery, o.DeliveryStage, m.Model, m.Brand, m.Images, o.OrderID, m.Price
            FROM Orders o
            JOIN Mobiles m ON o.MobileID = m.MobileID
            WHERE o.UserID = ? AND o.OrderStatus = 'Active' AND o.DeliveryStage != 'Delivered'
        """, (user_id,))
        rows = cursor.fetchall()
        orders = [{
            "ExpectedDelivery": row[0].strftime("%d-%m-%Y"),
            "DeliveryStage": row[1],
            "Model": row[2],
            "Brand": row[3],
            "Image": row[4],
            "OrderID": row[5],
            "Price": indian_format(row[6])
        } for row in rows]

        return render_template("track_order.html", user=user_data, orders=orders)

    except Exception as e:
        print("Track Order Error:", e)
        return render_template("track_order.html", user=user_data, orders=[])

    finally:
        cursor.close()

@app.route('/cancel-order', methods=['POST'])
def cancel_order():
    data = request.get_json()
    order_id = data.get("id")

    token = request.cookies.get("jwt")
    user_data = decode_token(token) if token else None

    if not user_data:
        return jsonify({"success": False, "message": "Unauthorized"}), 401

    cursor = conn.cursor()
    try:
        cursor.execute("SELECT UserID FROM Users WHERE Username = ?", (user_data["username"],))
        user_id = cursor.fetchone()[0]

        cursor.execute("""
            UPDATE Orders
            SET OrderStatus = 'Cancelled'
            WHERE UserID = ? AND OrderStatus = 'Active' AND DeliveryStage != 'Delivered' AND MobileID IN (
                SELECT MobileID FROM Mobiles WHERE OrderID = ?
            )
        """, (user_id, order_id))

        conn.commit()
        return jsonify({"success": True})
    except Exception as e:
        print("Cancel Order Error:", e)
        return jsonify({"success": False, "message": "Error cancelling order"})
    finally:
        cursor.close()

@app.route('/order-history')
def order_history():
    token = request.cookies.get("jwt")
    user_data = decode_token(token) if token else None

    if not user_data:
        return redirect("/")

    cursor = conn.cursor()
    try:
        cursor.execute("SELECT UserID FROM Users WHERE Username = ?", (user_data["username"],))
        user_id = cursor.fetchone()[0]

        cursor.execute("""
            SELECT m.Model, m.Brand, TO_CHAR(m.Price, '99,99,999'), TO_CHAR(o.OrderDate, 'DD-MM-YYYY'), a.DoorStreet, a.Locality, a.City, a.Country, a.Pincode, m.Images, TO_CHAR(o.ExpectedDelivery, 'DD-MM-YYYY'), o.OrderID
            FROM Orders o
            JOIN Mobiles m ON o.MobileID = m.MobileID
            JOIN UserAddresses a ON o.AddressID = a.AddressID
            WHERE o.UserID = ? AND o.DeliveryStage = 'Delivered'
            ORDER BY o.OrderDate DESC
        """, (user_id,))
        rows = cursor.fetchall()

        history = [{
            "Model": row[0],
            "Brand": row[1],
            "Price": row[2],
            "OrderDate": row[3],
            "DoorStreet": row[4],
            "Locality": row[5],
            "City": row[6],
            "Country": row[7],
            "Pincode": row[8],
            "Image": row[9],
            "DeliveryDate": row[10],
            "OrderID": row[11],
        } for row in rows]


        return render_template("order_history.html", user=user_data, history=history)

    except Exception as e:
        print("Order History Error:", e)
        return render_template("order_history.html", user=user_data, history=[])

    finally:
        cursor.close()

@app.route("/invoice/<int:order_id>")
def generate_invoice(order_id):
    token = request.cookies.get("jwt")
    user_data = decode_token(token) if token else None

    if not user_data:
        return redirect("/")

    cursor = conn.cursor()
    try:
        # Get order + address + mobile info
        cursor.execute("""
            SELECT m.Model, m.Brand, TO_CHAR(m.Price, '99,99,999'), TO_CHAR(o.OrderDate, 'DD-MM-YYYY'),
                   TO_CHAR(o.ExpectedDelivery, 'DD-MM-YYYY'), a.DoorStreet, a.Locality, a.City,
                   a.Country, a.Pincode, m.Images, u.Username, u.Email, u.Phone
            FROM Orders o
            JOIN Mobiles m ON o.MobileID = m.MobileID
            JOIN UserAddresses a ON o.AddressID = a.AddressID
            JOIN Users u ON o.UserID = u.UserID
            WHERE o.OrderID = ?
        """, (order_id,))
        row = cursor.fetchone()

        if not row:
            return "Invalid Order ID", 404

        invoice_data = {
            "Model": row[0],
            "Brand": row[1],
            "Price": row[2],
            "OrderDate": row[3],
            "DeliveryDate": row[4],
            "Address": f"{row[5]}, {row[6]}, {row[7]} - {row[9]}, {row[8]}",
            "Image": row[10],
            "Username": row[11],
            "Email": row[12],
            "Phone": row[13],
            "OrderID": order_id
        }

        return render_template("invoice.html", invoice=invoice_data)

    except Exception as e:
        return f"Error: {e}", 500
    finally:
        cursor.close()

# Set up background scheduler to check cart continuously
def start_discount_task():
    scheduler = BackgroundScheduler()
    scheduler.add_job(check_cart_and_send_discount_notifications, 'interval', minutes=10)  # Check every 10 minutes
    scheduler.start()

    print("Discount checker task started...")

def start_home():
    start_discount_task()
    print(""" * Debug mode: on \n * Running on http://127.0.0.1:5001 \nPress CTRL+C to quit""")
    app.run(port=5001, debug=True)

if __name__ == '__main__':
    # Run main app (Specify full path)
    subprocess.Popen(["python", "-c", "import mobiwiseinsight.app as home; home.start_home()"])  
    print("Main app started")

    # Run user form
    subprocess.Popen(["python", "-c", "import mobiwiseinsight.User_Authenticity_Form.app as user; user.start_user()"])
    print("User Authentication  form started")

    # Start admin authenticity form
    subprocess.Popen(["python", "-c", "import mobiwiseinsight.Admin_Authenticity_Form.app as admin; admin.start_admin()"])
    print("Admin Authentication form started")

    # Start mobile form
    subprocess.Popen(["python", "-c", "import mobiwiseinsight.Mobile_Form.app as mobile; mobile.start_mobile()"])
    print("Mobile form started")

    # Start admin form
    subprocess.Popen(["python", "-c", "import mobiwiseinsight.Admin_Form.app as admin; admin.start_admin_form()"])
    print("Admin form started")

    # Start discount form
    subprocess.Popen(["python", "-c", "import mobiwiseinsight.Discount_Form.app as discount; discount.start_discount_form()"])
    print("Discount form started")

    # Start order management form
    subprocess.Popen(["python", "-c", "import mobiwiseinsight.Order_Form.app as order; order.start_order_management()"])
    print("Order management form started")