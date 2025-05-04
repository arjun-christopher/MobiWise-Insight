import pywhatkit as kit
import time
from datetime import datetime, timedelta

def send_whatsapp_message(user_phone, model, discount_percentage, new_price, mobile_id):

    url = f"http://127.0.0.1:5001/mobile-details/{mobile_id}"
    # Format the message
    message = f"             📦 *MobiWise Insight* 📦             \n\n" \
              f"🚨 *Exclusive Offer!* 🚨\n\n" \
              f"Get your hands on the *{model}* 📱 at an unbeatable price!\n\n" \
              f"🎉 *{discount_percentage}% OFF!* 🎉\n\n" \
              f"🔥 *New Price*: ₹{new_price}\n\n" \
              f"🛒 *Hurry, Limited Offer!* Grab it now!\n\n" \
              f"Check the product below 👇\n" \
              f"{url}\n"  # Include URL in the message text

    # Send message immediately using pywhatkit without entering manually
    kit.sendwhatmsg_instantly(
        phone_no=user_phone,              # User's phone number
        message=message,                  # Formatted message
        wait_time=15                       # Wait 15 seconds before sending the message
    )

    print(f"Message sent to {user_phone} via WhatsApp Web!")


def send_order_confirmation_whatsapp(phone_number, username, expected_delivery, total_items, grand_total):
    try:
        message = f"""Hello {username},

✅ Your order has been placed successfully at *MobiWise Insight*! 

🛒 Total Items: {total_items}  
💰 Grand Total: ₹{grand_total}  
📦 Expected Delivery: {expected_delivery.strftime('%d-%b-%Y')}  

We’ll keep you updated about your delivery status.

Thank you for shopping with us!  
- MobiWise Insight Team"""

        # Format phone number (India example: +91XXXXXXXXXX)
        formatted_phone = f"{phone_number.strip()}"

        # Send message immediately using pywhatkit without entering manually
        kit.sendwhatmsg_instantly(
            phone_no=formatted_phone,              # User's phone number
            message=message,                  # Formatted message
            wait_time=15                       # Wait 15 seconds before sending the message
        )
        print(f"✅ WhatsApp confirmation sent to {formatted_phone}")

    except Exception as e:
        print(f"❌ WhatsApp message error: {e}")
