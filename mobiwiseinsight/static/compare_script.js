document.addEventListener("DOMContentLoaded", function () {
    generateComparisonSlots();
});

// Generate empty slots based on the selected number of mobiles
function generateComparisonSlots() {
    const comparisonContainer = document.getElementById("comparison-container");
    const mobileCount = document.getElementById("mobile-count").value;
    comparisonContainer.innerHTML = ""; // Clear previous slots

    for (let i = 0; i < mobileCount; i++) {
        let slot = document.createElement("div");
        slot.classList.add("mobile-slot");
        slot.innerHTML = `<span>+ Add Mobile</span>`;
        slot.onclick = () => openSearchPopup(i);
        comparisonContainer.appendChild(slot);
    }
}

// Open search popup
function openSearchPopup(slotIndex) {
    const searchPopup = document.getElementById("search-popup");
    searchPopup.style.display = "flex";
    searchPopup.dataset.slotIndex = slotIndex;
}

// Close search popup
function closeSearch() {
    document.getElementById("search-popup").style.display = "none";
}

// Fetch and display search results dynamically
function searchMobiles() {
    const searchPopupInput = document.querySelector("#search-popup input[type='text']");
    const searchResults = document.getElementById("search-results");
    let query = searchPopupInput.value.toLowerCase();

    fetch(`/search-mobiles`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query })
    })
    .then(response => response.json())
    .then(data => {
        searchResults.innerHTML = ""; // Clear previous results

        if (data.mobiles.length === 0) {
            searchResults.innerHTML = "<p>No mobiles found.</p>";
            return;
        }

        data.mobiles.forEach(mobile => {
            let item = document.createElement("div");
            item.classList.add("search-result-item");
            item.innerHTML = `<img src="${mobile.IMAGES}" width="50"> ${mobile.MODEL}`;
            item.onclick = () => selectMobile(mobile);
            searchResults.appendChild(item);
        });
    })
    .catch(error => console.error("Error fetching mobiles:", error));
}

// Assign selected mobile to a slot
function selectMobile(mobile) {
    let slotIndex = document.getElementById("search-popup").dataset.slotIndex;
    let slots = document.getElementsByClassName("mobile-slot");
    let slot = slots[slotIndex];

    slot.innerHTML = `<img src="${mobile.IMAGES}" alt="${mobile.MODEL}"><p>${mobile.MODEL}</p>`;
    slot.dataset.mobileId = mobile.MOBILEID;
    closeSearch();
    checkCompareButton();
}

// Enable compare button if all slots are filled
function checkCompareButton() {
    let filledSlots = [...document.getElementsByClassName("mobile-slot")].filter(slot => slot.dataset.mobileId);
    let compareButton = document.getElementById("compare-btn");
    compareButton.disabled = filledSlots.length < document.getElementById("mobile-count").value;
}

// Compare mobiles and display results
async function compareMobiles() {
    const mobileSlots = document.getElementsByClassName("mobile-slot");
    const selectedMobiles = [...mobileSlots]
        .map(slot => slot.dataset.mobileId)
        .filter(id => id);

    if (selectedMobiles.length < 2) {
        alert("Please select at least two mobiles to compare.");
        return;
    }

    const selectedPreferences = [...document.querySelectorAll(".preference-checkbox:checked")]
        .map(cb => cb.value);

    try {
        const response = await fetch("/compare-mobiles", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                mobile_ids: selectedMobiles,
                preferences: selectedPreferences
            })
        });

        const data = await response.json();

        if (data.error) {
            alert(data.error);
            return;
        }

        const mobileData = data.mobiles;
        const comparisons = data.comparisons;
        const suggestion = data.best_suggestion;

        const specsTable = document.getElementById("comparison-table");
        const outcomeTable = document.getElementById("comparison-outcome");
        const suggestionResult = document.getElementById("suggestion-result");

        // Clear previous data
        specsTable.innerHTML = "";
        outcomeTable.innerHTML = "";
        suggestionResult.innerHTML = "";

        // ✅ 1. Display Mobile Specifications
        let specsHeader = "<tr><th>Specification</th>";
        mobileData.forEach(m => {
            specsHeader += `<th>${m.Model}</th>`;
        });
        specsHeader += "</tr>";
        specsTable.innerHTML += specsHeader;

        const specMap = {
            "Price": "Price",
            "RAM": "RAM",
            "Storage": "Storage",
            "Battery": "Battery",
            "Display": "Display",
            "Processor": "Processor",
            "Front Camera": "FrontCamera",
            "Rear Camera": "RearCamera",
            "User Rating": "UserRating"
        };

        document.getElementById("specs_head").style.display = "block";
        for (const [label, key] of Object.entries(specMap)) {
            let row = `<tr><td>${label}</td>`;
            mobileData.forEach(m => {
                const val = key === "Price" ? "₹ " + m[key] : m[key];
                row += `<td>${val}</td>`;
            });
            row += "</tr>";
            specsTable.innerHTML += row;
        }

        // ✅ 2. Display Feature-Wise Best Comparison Outcome
        document.getElementById("outcome_head").style.display = "block";
        let outcomeHeader = "<tr><th>Feature</th><th>Best Mobile</th><th>Best Value</th></tr>";
        outcomeTable.innerHTML += outcomeHeader;

        comparisons.forEach(c => {
            outcomeTable.innerHTML += `
                <tr>
                    <td>${c.feature}</td>
                    <td class="best-spec">${c.best_model}</td>
                    <td>${c.feature === "Price" ? "" + c.best_value : c.best_value}</td>
                </tr>
            `;
        });

        // ✅ 3. Display Best Recommended Mobile
        if (suggestion && suggestion.model !== "N/A") {
            suggestionResult.innerHTML = `
                <h2>Best Recommended Mobile</h2>
                <div class="best-mobile">
                    <div class="best-mobile-info">
                        <p><strong>Model:</strong> ${suggestion.model}</p>
                        <p><strong>Brand:</strong> ${suggestion.brand}</p>
                        <p><strong>Price:</strong> ${suggestion.price}</p>
                        <p><strong>Why Recommended:</strong> ${suggestion.reason}</p>
                    </div>
                </div>
            `;
        }

        document.getElementById("create-link-btn").style.display = "inline-block";


    } catch (err) {
        console.error("Comparison Error:", err);
        alert("Error comparing mobiles. Please try again.");
    }
}

// Redirect to all mobiles when search box is clicked
function redirectToAllMobiles() {
    if (!window.location.pathname.includes("/all-mobiles")) {
        window.location.href = "/all-mobiles";
    }
}

function generateShareableLink() {
    const selectedMobiles = Array.from(document.querySelectorAll(".mobile-slot"))
        .map(slot => slot.dataset.mobileId)
        .filter(Boolean);

    const preferences = Array.from(document.querySelectorAll(".preference-checkbox:checked"))
        .map(checkbox => checkbox.value);

    fetch("/generate-compare-link", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ mobile_ids: selectedMobiles, preferences: preferences })
    })
    .then(res => res.json())
    .then(data => {
        if (data.link) {
            // Copy to clipboard
            navigator.clipboard.writeText(data.link).then(() => {
                showCopyPopup();
            });
        }
    })
    .catch(err => console.error("Link generation error:", err));
}

function showCopyPopup() {
    const popup = document.getElementById("copy-popup");
    popup.style.display = "block";

    // Force reflow for transition to work
    void popup.offsetWidth;

    popup.style.opacity = "1";

    setTimeout(() => {
        popup.style.opacity = "0";
        setTimeout(() => {
            popup.style.display = "none";
        }, 250); // match the transition duration
    }, 2500); // visible for 2.5 seconds
}
