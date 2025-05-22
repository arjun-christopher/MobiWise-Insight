// Global variables
let recognition;
let isListening = false;
let recognitionTimeout;
const MAX_SPEECH_DURATION = 30000; // 30 seconds max recording time
const SPEECH_PAUSE_DURATION = 3000; // 3 seconds of silence before stopping

// Initialize speech recognition
function initSpeechRecognition() {
    // Check if browser supports speech recognition
    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
        console.warn('Speech recognition not supported in this browser');
        return false;
    }

    // Create speech recognition instance
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    recognition = new SpeechRecognition();
    
    // Configure recognition
    recognition.continuous = true; // Changed to continuous for better handling
    recognition.interimResults = true; // Get interim results
    recognition.maxAlternatives = 1;
    recognition.lang = 'en-US';
    
    // Set longer silence detection
    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.interimResults = true; // Get interim results
    recognition.maxAlternatives = 1;

    // Handle results
    recognition.onresult = (event) => {
        clearTimeout(recognitionTimeout); // Clear any existing timeout
        
        // Get the latest result
        const result = event.results[event.resultIndex];
        const transcript = result[0].transcript;
        
        // Update input with latest transcript
        if (transcript.trim() !== '') {
            document.getElementById('chatbot-input').value = transcript;
        }
        
        // If this is a final result and not empty, send the message
        if (result.isFinal && transcript.trim() !== '') {
            // Auto-send the message if it's not empty
            setTimeout(() => {
                sendMessage();
                toggleListening(false);
            }, 500);
        } else if (!result.isFinal) {
            // If it's an interim result, set a timeout to handle pauses
            recognitionTimeout = setTimeout(() => {
                if (transcript.trim() !== '') {
                    sendMessage();
                }
                toggleListening(false);
            }, SPEECH_PAUSE_DURATION);
        }
    };

    // Handle errors
    recognition.onerror = (event) => {
        console.error('Speech recognition error:', event.error);
        clearTimeout(recognitionTimeout);
        
        // Don't show error if user manually stopped recording
        if (event.error === 'aborted' || event.error === 'not-allowed') {
            // Only show permission error if we were actually trying to listen
            if (event.error === 'not-allowed' && isListening) {
                addMessage('Please allow microphone access to use voice input.', 'error-message');
            }
        } else {
            addMessage('Voice input ended. You can try again or type your message.', 'info-message');
        }
        
        // Clean up
        toggleListening(false);
    };

    // Handle when recognition ends
    recognition.onend = () => {
        // Only restart if we're still supposed to be listening
        if (isListening) {
            try {
                recognition.start();
            } catch (e) {
                console.error('Error restarting recognition:', e);
                toggleListening(false); // Ensure we clean up if there's an error
            }
        } else {
            // Clean up the listening state
            document.getElementById('mic-button').classList.remove('listening');
            document.getElementById('chatbot-input').placeholder = 'Type your message or tap the mic...';
            
            // Remove any pulse indicators
            const pulseIndicators = document.querySelectorAll('.pulse');
            pulseIndicators.forEach(indicator => indicator.remove());
        }
    };

    return true;
}

// Toggle listening state
function toggleListening(forceStop = false) {
    const micButton = document.getElementById('mic-button');
    
    if (forceStop || isListening) {
        // Stop listening
        if (recognition) {
            recognition.stop();
        }
        isListening = false;
        micButton.classList.remove('listening');
        document.getElementById('chatbot-input').placeholder = 'Type your message or tap the mic...';
    } else {
        // Start listening
        if (!recognition && !initSpeechRecognition()) {
            addMessage('Voice input is not supported in your browser.', 'error-message');
            return;
        }
        
        try {
            // Clear any previous timeouts
            clearTimeout(recognitionTimeout);
            
            // Start recognition
            recognition.start();
            isListening = true;
            micButton.classList.add('listening');
            document.getElementById('chatbot-input').value = ''; // Clear previous input
            document.getElementById('chatbot-input').placeholder = 'Speak now...';
            
            // Add a small visual indicator that we're listening
            const indicator = document.createElement('div');
            indicator.className = 'pulse';
            micButton.appendChild(indicator);
            
            // Set a timeout for maximum recording duration
            recognitionTimeout = setTimeout(() => {
                if (isListening) {
                    const input = document.getElementById('chatbot-input').value;
                    if (input.trim() !== '') {
                        sendMessage();
                    } else {
                        addMessage('Listening timed out. Please try again.', 'info-message');
                    }
                    toggleListening(false);
                }
            }, MAX_SPEECH_DURATION);
            
        } catch (error) {
            console.error('Error starting speech recognition:', error);
            // Don't show error if it's because we're already listening
            if (error.toString().indexOf('already started') === -1) {
                addMessage('Error accessing microphone. Please ensure you have granted microphone permissions.', 'error-message');
            }
            isListening = false;
            micButton.classList.remove('listening');
            
            // Clean up any pulse indicators
            const pulseIndicators = document.querySelectorAll('.pulse');
            pulseIndicators.forEach(indicator => indicator.remove());
        }
    }
}

// Update mic button state based on listening state
function updateMicButton() {
    const micButton = document.getElementById('mic-button');
    if (!micButton) return;
    
    if (isListening) {
        micButton.innerHTML = '🎤';
    } else {
        micButton.innerHTML = '🎤';
    }
}

// Toggle chatbot visibility
function toggleChatbot() {
    const modal = document.getElementById('chatbot-modal');
    const isVisible = modal.style.display === 'flex';
    
    if (!isVisible) {
        // Show the chat
        modal.style.display = 'flex';
        // Initialize speech recognition when chat is opened
        initSpeechRecognition();
        // Focus the input field
        setTimeout(() => {
            document.getElementById('chatbot-input').focus();
        }, 100);
    } else {
        // Hide the chat
        modal.style.display = 'none';
        // Stop listening when chat is closed
        if (isListening) {
            toggleListening(true);
        }
    }
}

// Send message to chatbot
function sendMessage() {
    const input = document.getElementById('chatbot-input');
    const message = input.value.trim();
    
    if (message === '') return;
    
    // Add user message to chat
    addMessage(message, 'user-message');
    input.value = '';
    
    // Show typing indicator
    showTypingIndicator();
    
    // Send message to server
    fetch('/chatbot', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: message }),
    })
    .then(handleResponse)
    .catch(handleError);
}

// Show typing indicator
function showTypingIndicator() {
    const chatBody = document.getElementById('chatbot-body');
    const typingIndicator = document.createElement('div');
    typingIndicator.className = 'typing-indicator';
    typingIndicator.id = 'typing-indicator';
    typingIndicator.innerHTML = `
        <div class="dot"></div>
        <div class="dot"></div>
        <div class="dot"></div>
    `;
    chatBody.appendChild(typingIndicator);
    chatBody.scrollTop = chatBody.scrollHeight;
}

// Handle server response
function handleResponse(response) {
    if (!response.ok) {
        throw new Error('Network response was not ok');
    }
    return response.json().then(data => {
        // Remove typing indicator
        const indicator = document.getElementById('typing-indicator');
        if (indicator) {
            indicator.remove();
        }
        
        // Add bot response to chat
        if (data.reply) {
            // Split response by double newlines to handle paragraphs
            const paragraphs = data.reply.split('\n\n');
            paragraphs.forEach(para => {
                if (para.trim() !== '') {
                    addMessage(para, 'bot-message');
                }
            });
        } else {
            addMessage("I'm sorry, I couldn't process your request. Please try again later.", 'error-message');
        }
        
        // Scroll to bottom after message is added
        const chatBody = document.getElementById('chatbot-body');
        chatBody.scrollTop = chatBody.scrollHeight;
    });
}

// Handle errors
function handleError(error) {
    console.error('Error:', error);
    
    // Remove typing indicator
    const indicator = document.getElementById('typing-indicator');
    if (indicator) {
        indicator.remove();
    }
    
    // Show error message
    addMessage('An error occurred while processing your request. Please try again.', 'error-message');
    const chatBody = document.getElementById('chatbot-body');
    chatBody.scrollTop = chatBody.scrollHeight;
}

// Add message to chat with proper formatting
function addMessage(text, className) {
    const chatBody = document.getElementById('chatbot-body');
    const messageDiv = document.createElement('div');
    
    // Apply appropriate class and add message content
    messageDiv.className = className;
    
    // Check if the text contains any markdown-like formatting
    // This is a simple implementation - you might want to use a proper markdown parser
    let formattedText = text
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>') // Bold
        .replace(/\*(.*?)\*/g, '<em>$1</em>') // Italic
        .replace(/`([^`]+)`/g, '<code>$1</code>') // Inline code
        .replace(/\n/g, '<br>'); // New lines
    
    // Handle bullet points and numbered lists (very basic support)
    formattedText = formattedText.replace(/^\s*[-*]\s+(.*)$/gm, '• $1<br>');
    
    messageDiv.innerHTML = formattedText;
    
    // Add timestamp
    const timestamp = document.createElement('div');
    timestamp.className = 'message-timestamp';
    timestamp.textContent = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    messageDiv.appendChild(timestamp);
    
    chatBody.appendChild(messageDiv);
    
    // Scroll to bottom
    chatBody.scrollTop = chatBody.scrollHeight;
}

// Initialize event listeners when the DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Add click outside functionality
    document.addEventListener('click', function(event) {
        const chatbotModal = document.getElementById('chatbot-modal');
        const chatbotButton = document.getElementById('chatbot-button');
        
        // If the click is outside the chatbot modal and not on the button
        if (chatbotModal.style.display === 'flex' && 
            !chatbotModal.contains(event.target) && 
            event.target !== chatbotButton) {
            toggleChatbot();
        }
    });

    // Handle Enter key in input
    const input = document.getElementById('chatbot-input');
    if (input) {
        input.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                sendMessage();
            }
        });
    }
    
    // Close chat when clicking outside
    document.addEventListener('click', function(event) {
        const modal = document.getElementById('chatbot-modal');
        const chatButton = document.getElementById('chatbot-button');
        
        if (event.target === modal && !modal.contains(event.target) && event.target !== chatButton && !chatButton.contains(event.target)) {
            modal.style.display = 'none';
            if (isListening) {
                toggleListening(true);
            }
        }
    });
    
    // Initialize welcome message if chat is opened by default
    const modal = document.getElementById('chatbot-modal');
    if (modal && modal.style.display === 'flex') {
        // This will be handled by the server-side template
    }
});
