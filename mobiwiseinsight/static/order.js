function checkout() {
    document.getElementById("checkout-modal").style.display = "block";

    // Fill user details from DOM (server-side rendered)
    const username = document.getElementById('user_name').value;
    const email = document.querySelector("#profile-dropdown p:nth-child(2) strong")?.innerText || "";
    const phone = document.getElementById('phone').value;

    document.getElementById("user-name").value = username;
    document.getElementById("user-email").value = email;
    // You can fetch phone from backend if needed, for now keeping it blank
    document.getElementById("user-phone").value = phone;

    // Populate items
    const cartItems = document.querySelectorAll(".cart-item");
    const list = document.getElementById("checkout-items-list");
    list.innerHTML = "";

    cartItems.forEach(item => {
        const img = item.querySelector("img").src;
        const model = item.querySelector("h3").innerText;
        const price = item.querySelector(".cart-item-price").innerText;
        const mobileID = item.querySelector("button").getAttribute("data-value");

        const li = document.createElement("li");
        li.innerHTML = `
            <div style="display: flex; align-items: center;">
            <!-- Image on the Left -->
            <img src="${img}" style="width: 60px; height: auto; border-radius: 5px; margin-right: 80px;">
            
            <!-- Model on the Right (Vertically Centered) -->
            <strong style="flex: 0.8; font-size: 16px;">${model}</strong> -  ${price}

            <input type="hidden" class="mobile-id" value="${mobileID}">
        </div>
        <br>
        `;
        list.appendChild(li);
    });
}

function closeCheckoutModal() {
    document.getElementById("checkout-modal").style.display = "none";
}

// Optional: Close on outside click
window.onclick = function(event) {
    const modal = document.getElementById("checkout-modal");
    if (event.target == modal) {
        closeCheckoutModal();
    }
}

document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("checkout-form");

    form.addEventListener("submit", async function (e) {
        e.preventDefault(); // Prevent default form submission

        const address = {
            door_street: document.getElementById("door-street").value,
            locality: document.getElementById("locality").value,
            city: document.getElementById("city").value,
            country: document.getElementById("country").value,
            pincode: document.getElementById("pincode").value
        };

        const paymentMethod = document.getElementById("payment-method").value;

        const mobileIDs = Array.from(document.querySelectorAll(".mobile-id")).map(input => input.value);

        const orderData = {
            address: address,
            payment_method: paymentMethod,
            order_status: "Active",
            delivery_stage: "Dispatched",
            mobile_ids: mobileIDs
        };

        try {
            const response = await fetch("/checkout", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(orderData)
            });

            const result = await response.json();

            if (result.success) {
                alert("✅ Order placed successfully!");
            } else {
                alert("❌ " + result.message);
            }
        } catch (error) {
            console.error("Checkout error:", error);
            alert("Something went wrong while placing your order.");
        }
    });
});
