// Function to remove an item from the cart// Function to remove an item from the cart
function removeFromCart(button) {
    const mobileId = button.getAttribute('data-value'); // Get mobileId from the clicked button
    fetch('/remove-from-cart', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ mobile_id: mobileId })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            location.reload();  // Reload the page to update the cart
        } else {
            alert("Error removing item from cart.");
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
}


// Function to update the cart items and display total items and grand total
function updateCartDetails() {
    fetch('/cart')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Update total items count
                document.getElementById('total-items').innerText = data.totalItems;
                
                // Update grand total
                document.getElementById('grand-total').innerText = data.grandTotal;
                
                // Display cart items in the cart page
                const cartItemsList = document.getElementById('cart-items-list');
                cartItemsList.innerHTML = ''; // Clear the list before adding new items
                
                data.cartItems.forEach(item => {
                    let cartItemElement = document.createElement('li');
                    cartItemElement.classList.add('cart-item');
                    
                    cartItemElement.innerHTML = `
                        <a href="/mobile-details/${item.mobile_id}" class="cart-item-link">
                            <div class="cart-item-image">
                                <img src="${item.image}" alt="${item.model}">
                            </div>
                            <div class="cart-item-details">
                                <h3>${item.model}</h3>
                                <p class="cart-item-brand">${item.brand}</p>
                                <p class="cart-item-price">₹${item.price}</p>
                            </div>
                        </a>
                        <button class="cart-item-remove" data-value="${item.mobile_id}" onclick="removeFromCart(this)">Remove</button>
                    `;
                    cartItemsList.appendChild(cartItemElement);
                });
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
}


// Call updateCartDetails function when the page is loaded
document.addEventListener("DOMContentLoaded", function() {
    updateCartDetails();
});

// Check if the current page is the cart page
if (window.location.pathname === '/cart') {
    document.getElementById("cart-icon").classList.add("active");
}