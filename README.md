# MobiWise Insight - Mini-Project

## Overview
MobiWise Insight is a comprehensive platform for mobile management, e-commerce, and user engagement. It combines a Flask web application with AI-powered features, messaging utilities, and a Pygame-based mini-game. The project is modular, supporting admin/user authentication, order/discount/mobile management, and interactive features for both users and administrators.

## Key Features

### 1. User & Admin Authentication
- Secure JWT-based login and signup for users and admins
- Password management and session handling

### 2. Mobile Catalog & Management
- Browse, search, and filter a comprehensive mobile catalog
- View detailed mobile specifications and images
- Admins can add, update, or remove mobile entries

### 3. Cart & Order Processing
- Add/remove mobiles to/from cart
- Checkout and place orders with address management
- Track order status and view order history
- Generate downloadable invoices for completed orders

### 4. Discount & Offer Management
- Admins can create/manage discount campaigns
- Users receive notifications for eligible discounts
- Automated discount ad image generation using AI

### 5. AI-Powered Insights
- **Mobile Comparison:** Users can compare mobiles and receive AI-driven recommendations tailored to their preferences (using Gemini/Google Generative AI)
- **Chatbot:** Integrated chatbot answers user questions about mobiles, features, and recommendations

### 6. Notifications & Messaging
- **Email:** Order confirmations and notifications via SMTP
- **WhatsApp:** Automated WhatsApp messages for order and discount alerts (using pywhatkit)

### 7. News & Updates
- Fetches and displays the latest mobile news for users

### 8. Pygame Mini-Game
- Fun, custom mini-game themed around mobile devices (playable via `programs/test.py`)

### 9. Admin Dashboard
- Separate admin interfaces for managing users, mobiles, orders, and discounts
- Real-time analytics and logs for monitoring activity

### 10. Scheduled Tasks
- Background scheduler (APScheduler) checks carts and sends notifications periodically

## Project Structure
- `mobiwiseinsight/` - Main app
- `Admin_Authenticity_Form/`, `User_Authenticity_Form/`, `Order_Form/`, `Discount_Form/`, `Mobile_Form/`, `Admin_Form/` - Modular form and admin apps
- `programs/` - Utilities for AI, messaging, and mini-game
- `templates/` - Jinja2 HTML templates for all user/admin pages
- `static/` - CSS, JS, images, and game assets
- `Documents/` - Contains project documentation:
  - Requirements and design docs: SRS, SDS, project proposal, implementation/coding, software test case generation, decomposition, entity relationship diagram (PDF/DOCX)
  - Architecture diagrams, flowcharts, activity charts, task charts, module diagrams, use cases (draw.io and PNG)
  - Presentations (PPTX)
  - Images, icons, and logos (PNG)
  - Advertisement video (MP4)
  - `SRS References/` subfolder: supporting/reference materials
  - Useful for understanding system design, requirements, branding, and implementation details
- `requirements.txt` - Python dependencies

## Installation
1. **Clone the repository:**
   ```
   git clone <repo-url>
   cd MobiWise Insight - Mini-Project/mobiwiseinsight
   ```
2. **Install dependencies:**
   ```
   pip install -r requirements.txt
   ```
3. **Set up environment variables:**
   - Add DB credentials, email settings, and API keys as environment variables for security

## Usage
- **Run the Flask app:**
  ```
  python app.py
  ```
- **Play the Pygame mini-game:**
  ```
  python programs/test.py
  ```
- **Locust Performance Testing:**
  - A `locustfile.py` is included for load testing the main endpoints of the web application.
  - To run Locust and simulate user traffic on the web app, use:
    ```
    locust -f mobiwiseinsight/locustfile.py --host=http://localhost:5001
    ```
    Then open [http://localhost:8089](http://localhost:8089) in your browser to access the Locust web UI.

## Dependencies
See `requirements.txt` for the full list, including:
- Flask, flask-compress, flask-caching
- pyodbc
- requests
- apscheduler
- python-jwt
- pywhatkit
- pygame
- smtplib, email
- python-decimal
- uuid, logging
- google-generativeai

## Masked Credentials & Secrets
For security, all sensitive credentials, API keys, tokens, and secrets in this codebase have been replaced with `****MASKED****`.

**To run this project, you must replace all `****MASKED****` placeholders with your own valid values.**

### How to Update Masked Values
1. **Find all `****MASKED****` placeholders** in the codebase. These are used for:
   - Database credentials
   - Email/SMTP credentials
   - API keys and tokens (Gemini, Google GenerativeAI, Twilio, Hugging Face, News APIs, etc.)
   - Any other sensitive values
2. **Replace each `****MASKED****`** with your actual secret value (e.g., API key, token, password, etc.).
   - Never commit real secrets to public repositories.
   - Consider using environment variables or a `.env` file for sensitive data in production.

**Example:**
```python
API_KEY = "****MASKED****"  # Replace with your actual API key
```

**Replace with:**
```python
API_KEY = "your-real-api-key-here"
```

If you have any questions about which values to replace or best practices for secret management, see the Security section above or contact the author.

## Security
- Store sensitive data (DB credentials, API keys) in environment variables
- JWT is used for authentication and session management

## License
This project is for educational purposes. For commercial use, contact the author.

---
_Last updated: 2025-05-04_