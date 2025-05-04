from locust import HttpUser, task, between
import random

class WebsiteUser(HttpUser):
    wait_time = between(1, 2)

    # --- Main app endpoints ---
    @task
    def homepage(self):
        self.client.get("/")

    @task
    def latest_news(self):
        self.client.get("/latest-news")

    @task
    def latest_news_page(self):
        self.client.get("/latest-news/page")

    @task
    def all_mobiles(self):
        self.client.get("/all-mobiles")

    @task
    def cart(self):
        self.client.get("/cart")

    @task
    def order_history(self):
        self.client.get("/order-history")

    @task
    def search_mobiles(self):
        self.client.post("/search-mobiles", json={"query": random.choice(["Samsung", "Apple", "OnePlus"])})

    @task
    def filter_mobiles(self):
        self.client.post("/filter-mobiles", json={"brand": random.choice(["Apple", "Samsung"]), "price_min": 10000, "price_max": 50000})

    @task
    def compare_mobiles(self):
        self.client.post("/compare-mobiles", json={"mobiles": [random.randint(1, 10), random.randint(11, 20)]})

    @task
    def chatbot(self):
        self.client.post("/chatbot", json={"message": random.choice(["Hi!", "Tell me about iPhones", "What is the best deal?"])})

    @task
    def add_to_cart(self):
        self.client.post("/add-to-cart", json={"mobile_id": random.randint(1, 20)})

    @task
    def remove_from_cart(self):
        self.client.post("/remove-from-cart", json={"mobile_id": random.randint(1, 20)})

    @task
    def checkout(self):
        self.client.post("/checkout", json={"address_id": 1, "payment_method": "COD"})

    # --- User Auth endpoints ---
    @task
    def login(self):
        self.client.post("/login", json={"username": "testuser", "password": "testpass"})

    @task
    def signup(self):
        self.client.post("/signup", json={"username": "testuser", "password": "testpass", "email": "test@example.com"})

    @task
    def change_password(self):
        self.client.post("/change_password", json={"username": "testuser", "old_password": "testpass", "new_password": "newpass"})

    @task
    def request_otp(self):
        self.client.post("/request_otp", json={"username": "testuser"})

    @task
    def validate_otp(self):
        self.client.post("/validate_otp", json={"username": "testuser", "otp": "123456"})

    @task
    def update_password(self):
        self.client.post("/update_password", json={"username": "testuser", "new_password": "newpass"})

    # --- Discount endpoints ---
    @task
    def fetch_discount_record(self):
        self.client.post("/fetch_discount_record", json={"discount_id": 1})

    @task
    def save_discount(self):
        self.client.post("/save_discount", json={"discount_id": 1, "amount": 1000})

    @task
    def update_discount(self):
        self.client.post("/update_discount", json={"discount_id": 1, "amount": 1200})

    @task
    def delete_discount(self):
        self.client.post("/delete_discount", json={"discount_id": 1})

    # --- Mobile buffer endpoints ---
    @task
    def fetch_mobile_buffer(self):
        self.client.post("/fetch_mobile_buffer", json={"mobile_id": 1})

    @task
    def save_mobile_buffer(self):
        self.client.post("/save_mobile_buffer", json={"mobile_id": 1, "data": "buffer"})

    @task
    def update_mobile_buffer(self):
        self.client.post("/update_mobile_buffer", json={"mobile_id": 1, "data": "updated buffer"})

    @task
    def delete_mobile_buffer(self):
        self.client.post("/delete_mobile_buffer", json={"mobile_id": 1})
