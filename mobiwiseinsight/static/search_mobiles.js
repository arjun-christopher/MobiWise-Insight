document.addEventListener("DOMContentLoaded", function () {
    const searchBar = document.getElementById("search-bar");
    const searchButton = document.getElementById("search-btn");
    const mobilesContainer = document.querySelector(".mobiles-container");

    async function fetchSearchResults(query) {
        const response = await fetch("/search-mobiles", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ query })
        });
        
        const data = await response.json();
        mobilesContainer.innerHTML = ""; // Clear previous results

        if (data.mobiles.length === 0) {
            mobilesContainer.innerHTML = "<p>No mobiles found.</p>";
            return;
        }

        data.mobiles.forEach(mobile => {
            let mobileCard = document.createElement("a");
            mobileCard.href = `/mobile-details/${mobile.MOBILEID}`;
            mobileCard.classList.add("mobile-card", "fade-in");

            mobileCard.innerHTML = `
                <div class="mobile-image">
                    <img src="${mobile.IMAGES}" alt="${mobile.MODEL}">
                </div>
                <div class="mobile-details">
                    <h3>${mobile.MODEL}</h3>
                    <p class="brand">${mobile.BRAND}</p>
                    <p class="price">₹${mobile.PRICE}</p>
                </div>
            `;
            mobilesContainer.appendChild(mobileCard);
        });
    }

    // **Real-time search as user types**
    searchBar.addEventListener("input", function () {
        fetchSearchResults(searchBar.value);
    });

    // **Fetch results when search button is clicked**
    searchButton.addEventListener("click", function () {
        fetchSearchResults(searchBar.value);
    });

    // **Fetch results on Enter key press**
    searchBar.addEventListener("keypress", function (event) {
        if (event.key === "Enter") {
            fetchSearchResults(searchBar.value);
        }
    });
});

function redirectToAllMobiles() {
    // Check if the current page is NOT 'all-mobiles'
    if (!window.location.pathname.includes("/all-mobiles")) {
        window.location.href = "/all-mobiles"; // Redirect only if not already on 'all-mobiles.html'
    }
}
