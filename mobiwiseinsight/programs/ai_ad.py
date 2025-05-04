import requests
import time
import os

# Hugging Face API config
API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-3.5-large"
HEADERS = {
    "Authorization": "Bearer ****MASKED****",  # Replace with your actual token
    "Content-Type": "application/json"
}

# Retry-enabled query function
def query_huggingface(payload):
    response = requests.post(API_URL, headers=HEADERS, json=payload)

    if response.status_code == 503:
        print("⚠️ Model is loading, retrying in 10 seconds...")
        time.sleep(10)
        return query_huggingface(payload)

    if not response.ok:
        print(f"❌ Error {response.status_code}: {response.text}")
        return None

    return response.content


# Main function to process all discount entries
def generate_all_discount_ads(discount_data):
    """
    discount_data: List of tuples (MobileID, Model, ImageURL, OfferName, Discount%, Price)
    """
    discount_img_path = 'mobiwiseinsight/static/discount_images/'
    os.makedirs(discount_img_path, exist_ok=True)

    rendered_data = []

    for row in discount_data:
        mobile_id, model, img_url, offer_name, discount_percent, price = row
        filename = f"{mobile_id}.jpg"
        save_path = os.path.join(discount_img_path, filename)

        # Prompt: generate a visually compelling ad
        prompt = generate_fancy_prompt(model, offer_name, discount_percent, price)

        # Generate image
        image_bytes = query_huggingface({"inputs": prompt})

        if image_bytes:
            with open(save_path, "wb") as f:
                f.write(image_bytes)
            print(f"✅ Ad image saved for {model} at {save_path}")
        else:
            print(f"❌ Failed to generate image for {model}")
            continue

        # Append data for rendering
        rendered_data.append({
            "id": mobile_id,
            "model": model,
            "discount": discount_percent,
            "price": price,
            "offer": offer_name,
            "image_path": f"/static/discount_images/{filename}"
        })

    return rendered_data


# Prompt generator for Hugging Face
def generate_fancy_prompt(model, offer_name, discount_percent, price):
    return (
        f"""A luxurious, futuristic mobile discount advertisement featuring the {model} smartphone.
The scene is set in an ultra-modern tech showroom with sleek, reflective surfaces and dynamic lighting. Glowing, animated digital banners hover above the phone display, showcasing the latest technology.
The smartphone is showcased on a rotating platform, emphasizing its sleek design, smooth edges, and vibrant display.
Prominently display the text: '{offer_name} and {discount_percent}% OFF' in a bold, 3D-glowing neon font, with the discount percentage pulsing for attention.
The final price, '₹{price}', appears in a large, metallic gradient font with a shiny gold finish, positioned below the phone in a clean, professional layout.
Use a high-tech digital theme with bright accents like electric blue, neon purple, and glowing orange.
Incorporate motion blur effects for a futuristic, fast-paced feel.
Add dynamic reflections on the showroom floor and subtle animated sparks to suggest premium quality.
Ensure the design is ultra-sharp, highly detailed, and suitable for social media promotion, including platforms like Instagram and Facebook.
Maintain a professional and luxurious style while ensuring the smartphone remains the focal point of the image.
Use fancy lighting, vibrant contrast, and cinematic framing to create an eye-catching visual that highlights the discount and premium nature of the offer.""")
