from twilio.rest import Client

# Twilio Credentials (Replace with your actual credentials)
ACCOUNT_SID = "****MASKED****"
AUTH_TOKEN = "****MASKED****"
TWILIO_PHONE_NUMBER = "****MASKED****"

# Initialize Twilio Client
client = Client(ACCOUNT_SID, AUTH_TOKEN)

def send_sms(otp, phone):
    # Message to be sent
    message_body = f"OTP: {otp}"

    # Send SMS
    message = client.messages.create(
        body=message_body,
        from_=TWILIO_PHONE_NUMBER,
        to=phone
    )

    # Print message SID for tracking
    print(f"Message sent successfully! Message SID: {message.sid}")
    return True
