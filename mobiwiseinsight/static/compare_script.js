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
                    <button onclick="speakSuggestion()" style="
                        margin-top: 10px;
                        padding: 10px 20px;
                        background-color: #00b4d8;
                        color: white;
                        border: none;
                        border-radius: 25px;
                        cursor: pointer;
                        font-weight: bold;
                        font-size: 14px;
                        transition: all 0.3s ease;
                        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                    " onmouseover="this.style.backgroundColor='#0077b6'; this.style.transform='translateY(-2px)'; this.style.boxShadow='0 4px 8px rgba(0,0,0,0.15)'"
                    onmouseout="this.style.backgroundColor='#00b4d8'; this.style.transform='translateY(0)'; this.style.boxShadow='0 2px 5px rgba(0,0,0,0.1)'"
                    onmousedown="this.style.transform='translateY(0)'; this.style.boxShadow='0 1px 3px rgba(0,0,0,0.1)'"
                    onmouseup="this.style.transform='translateY(-2px)'; this.style.boxShadow='0 4px 8px rgba(0,0,0,0.15)'">
                        Hear Suggestion
                    </button>
                </div>
            `;
        }

        // ✅ 4. Build Pie Chart from Feature Wins
        document.getElementById("chart_head").style.display = "block";
        const featureCounts = {};
        const featureMap = {};
        
        comparisons.forEach(c => {
            let rawModels = [];
        
            // ✅ If best_model is array, use as is
            if (Array.isArray(c.best_model)) {
                rawModels = c.best_model;
            } else if (typeof c.best_model === "string") {
                // ✅ Split combined string by known separators
                rawModels = c.best_model.split(/\/|&|,/).map(m => m.trim());
            }
        
            // ✅ Filter out invalid entries (e.g., chipset names, empty strings)
            rawModels.forEach(model => {
                // Only allow known models present in `data.mobiles`
                const isValidModel = data.mobiles.some(m => m.Model === model);

                if (!isValidModel || !model) return;

        
                featureCounts[model] = (featureCounts[model] || 0) + 1;
                if (!featureMap[model]) featureMap[model] = [];
                featureMap[model].push(c.feature);
            });
        });
        
        
        // Prepare chart data
        const labels = Object.keys(featureCounts);
        const dataValues = Object.values(featureCounts);

        // Chart Setup with Custom Tooltip
        const ctx = document.getElementById("featureWinsChart").getContext("2d");
        if (window.featureChart) window.featureChart.destroy(); // clear previous

        window.featureChart = new Chart(ctx, {
            type: 'pie',
            data: {
                labels: Object.keys(featureCounts),
                datasets: [{
                    label: "Feature Wins",
                    data: Object.values(featureCounts),
                    backgroundColor: [
                        '#0077b6', '#00b4d8', '#90e0ef', '#caf0f8',
                        '#f9c74f', '#f9844a', '#f94144', '#43aa8b'
                    ],
                    borderColor: '#fff',
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                animation: {
                    animateScale: true,
                    animateRotate: true,
                    duration: 1500,
                    easing: 'easeOutBounce'
                },
                plugins: {
                    tooltip: {
                        callbacks: {
                            label: function (context) {
                                const model = context.label;
                                const count = context.formattedValue;
                                const features = featureMap[model] || [];
                                return [
                                    `Features Won: ${count}`
                                ];
                            }
                        }
                    },
                    legend: {
                        position: 'bottom'
                    },
                    title: {
                        display: true,
                        text: 'Which Mobile Wins More Features?'
                    }
                }
            }
        });

        // ✅ 5. Feature Breakdown Section (Responsive Tags Layout)
        const breakdownContainer = document.getElementById("feature-breakdown");
        breakdownContainer.innerHTML = '<h4 style="font-size: 1.2em; margin-bottom: 10px;">Feature Wins by Model</h4>';


        Object.entries(featureMap).forEach(([model, features]) => {
            breakdownContainer.innerHTML += `
                <div style="margin-bottom: 20px;">
                    <strong>${model}</strong>
                    <div class="feature-tags" style="
                        display: flex;
                        gap: 6px;
                        margin-top: 8px;
                        background-color: #f9f9f9;
                        padding: 10px;
                        border-radius: 8px;
                    ">
                        ${features.map(f => `<span style="
                            background-color: var(--light-blue);
                            padding: 6px 12px;
                            border-radius: 16px;
                            font-size: 14px;
                            color: white;
                            white-space: nowrap;
                        ">${f}</span>`).join('')}
                    </div>
                </div>
            `;
        });

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

// Voice configuration
const VOICE_STORAGE_KEY = 'mobiwiseVoice';
let currentVoice = null;
let voicesLoaded = false;

// Load voices when the page loads
function loadVoices() {
    return new Promise((resolve) => {
        const voices = window.speechSynthesis.getVoices();
        if (voices.length) {
            voicesLoaded = true;
            console.log('Voices loaded on page load:', voices);
            resolve(voices);
        } else {
            // Some browsers need this event to load voices
            window.speechSynthesis.onvoiceschanged = () => {
                const voices = window.speechSynthesis.getVoices();
                console.log('Voices loaded via onvoiceschanged:', voices);
                voicesLoaded = true;
                resolve(voices);
            };
        }
    });
}

function saveVoice(voice) {
    if (!voice || !voice.voiceURI) return;
    
    currentVoice = voice;
    const voiceData = {
        voiceURI: voice.voiceURI,
        name: voice.name,
        lang: voice.lang
    };
    
    try {
        sessionStorage.setItem(VOICE_STORAGE_KEY, JSON.stringify(voiceData));
        console.log('Voice saved:', voiceData);
    } catch (e) {
        console.error('Error saving voice:', e);
    }
}

async function findVoice() {
    console.log('Finding voice...');
    
    // Wait for voices to load
    const voices = await loadVoices();
    
    if (!voices || voices.length === 0) {
        console.error('No voices available');
        return null;
    }

    console.log('All available voices:', voices);

    // 1. Check if current voice is still available
    if (currentVoice) {
        const voice = voices.find(v => v.voiceURI === currentVoice.voiceURI);
        if (voice) {
            console.log('Using current voice:', voice);
            return voice;
        }
    }

    // 2. Try to load from session storage
    try {
        const savedData = sessionStorage.getItem(VOICE_STORAGE_KEY);
        if (savedData) {
            const savedVoice = JSON.parse(savedData);
            console.log('Loaded saved voice data:', savedVoice);
            
            // Find the saved voice in available voices
            const voice = voices.find(v => v.voiceURI === savedVoice.voiceURI);
            if (voice) {
                console.log('Using saved voice:', voice);
                currentVoice = voice;
                return voice;
            }
            console.log('Saved voice not found in available voices');
        } else {
            console.log('No saved voice data found');
        }
    } catch (e) {
        console.error('Error loading saved voice:', e);
    }

    // If no saved voice or it's not available, find a new female voice
    const femaleVoices = voices.filter(voice => {
        const name = voice.name.toLowerCase();
        return (
            name.includes('female') || 
            name.includes('zira') ||
            name.includes('susan') ||
            name.includes('hazel') ||
            name.includes('eva') ||
            name.includes('google uk english female') ||
            name.includes('google us english female') ||
            name.includes('microsoft zira desktop') ||
            (voice.gender && voice.gender.toLowerCase() === 'female')
        ) && voice.lang.includes('en');
    });
    
    if (femaleVoices.length > 0) {
        // Save the first matching female voice
        const selectedVoice = femaleVoices[0];
        console.log('Selected female voice:', selectedVoice);
        saveVoice(selectedVoice);
        return selectedVoice;
    }
    
    // Fallback to any English voice
    const englishVoices = voices.filter(voice => voice.lang.includes('en'));
    if (englishVoices.length > 0) {
        const selectedVoice = englishVoices[0];
        console.log('Selected English voice:', selectedVoice);
        saveVoice(selectedVoice);
        return selectedVoice;
    }
    
    // Last resort: use the first available voice
    if (voices.length > 0) {
        console.log('Using first available voice:', voices[0]);
        saveVoice(voices[0]);
        return voices[0];
    }
    
    console.error('No suitable voice found');
    return null;
}

// Track if speech is currently active
let isSpeaking = false;

async function speakSuggestion() {
    console.log('Speak button clicked');
    
    // If already speaking, stop and return
    if (isSpeaking) {
        window.speechSynthesis.cancel();
        isSpeaking = false;
        updateButtonText(false);
        console.log('Speech stopped by user');
        return;
    }
    
    try {
        // Get the mobile info div (exclude the button)
        const mobileInfoDiv = document.querySelector('.best-mobile .best-mobile-info');
        if (!mobileInfoDiv) {
            console.error('No suggestion content found');
            alert('No suggestion available to read');
            return;
        }
        
        // Extract only the text content from the mobile info div
        const suggestionText = mobileInfoDiv.innerText || mobileInfoDiv.textContent;
        if (!suggestionText || suggestionText.trim() === '') {
            console.error('Empty suggestion text');
            alert('No text content found to read');
            return;
        }
        
        console.log('Text to speak:', suggestionText);
        
        // Create speech utterance
        const msg = new SpeechSynthesisUtterance(suggestionText);
        msg.volume = 1; // 0 to 1
        msg.rate = 0.9; // Slightly slower rate for better clarity
        msg.pitch = 1;
        msg.lang = 'en-US';
        
        // Find and set the voice
        const selectedVoice = await findVoice();
        if (!selectedVoice) {
            console.error('No suitable voice found');
            alert('No suitable voice found. Please check your text-to-speech settings.');
            return;
        }
        
        console.log('Selected voice:', selectedVoice);
        msg.voice = selectedVoice;
        
        // Save the selected voice for future use
        saveVoice(selectedVoice);
        
        // Set up event handlers
        msg.onstart = () => {
            isSpeaking = true;
            updateButtonText(true);
            console.log('Speech started');
        };
        
        msg.onend = () => {
            isSpeaking = false;
            updateButtonText(false);
            console.log('Speech ended');
        };
        
        msg.onerror = (event) => {
            console.error('Speech error:', event);
            isSpeaking = false;
            updateButtonText(false);
            
            // If there's an error, clear the saved voice
            if (event.error === 'synthesis-failed') {
                console.log('Clearing saved voice due to error');
                sessionStorage.removeItem(VOICE_STORAGE_KEY);
                currentVoice = null;
            }
        };
        
        // Start speaking
        console.log('Starting speech synthesis...');
        window.speechSynthesis.speak(msg);
        
    } catch (error) {
        console.error('Error in speakSuggestion:', error);
        isSpeaking = false;
        updateButtonText(false);
        alert('An error occurred while trying to read the suggestion.');
    }
}

// Update button text based on speaking state
function updateButtonText(isSpeaking) {
    const buttons = document.querySelectorAll('button[onclick="speakSuggestion()"]');
    buttons.forEach(button => {
        button.textContent = isSpeaking ? 'Stop Speaking' : 'Hear Suggestion';
    });
    
    // Also update the button in the suggestion result if it exists
    const suggestionButton = document.querySelector('.best-mobile button');
    if (suggestionButton) {
        suggestionButton.textContent = isSpeaking ? 'Stop Speaking' : 'Hear Suggestion';
    }
}
