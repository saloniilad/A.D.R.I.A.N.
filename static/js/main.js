class JarvisUI {
    constructor() {
        this.chatMessages = document.getElementById('chatMessages');
        this.userInput = document.getElementById('userInput');
        this.micButton = document.getElementById('micButton');
        this.sendButton = document.getElementById('sendButton');
        this.statusIndicator = document.getElementById('statusIndicator');
        this.statusDot = this.statusIndicator.querySelector('.status-dot');
        this.statusText = this.statusIndicator.querySelector('.status-text');
        
        this.isListening = false;
        this.recognition = null;
        this.isTyping = false;
        this.isSpeaking = false;
        
        // Text-to-Speech setup
        this.speechSynthesis = window.speechSynthesis;
        this.currentUtterance = null;
        this.voiceSettings = {
            rate: 0.9,
            pitch: 1.0,
            volume: 0.8
        };
        
        this.initializeEventListeners();
        this.initializeSpeechRecognition();
        this.initializeTextToSpeech();
        this.updateStatus('Ready', 'ready');
        
        // Welcome message
        setTimeout(() => {
            const welcomeMessage = "Hello! I'm Jarvis, your personal AI assistant. I can help you with calculations, provide information from Wikipedia, tell jokes, show the current time and date, open websites, and much more. How can I assist you today?";
            this.addMessage(welcomeMessage, 'assistant');
            this.speakText(welcomeMessage);
        }, 500);
    }

    initializeEventListeners() {
        // Send button click
        this.sendButton.addEventListener('click', () => this.sendMessage());
        
        // Enter key press (Shift+Enter for new line)
        this.userInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });
        
        // Input changes
        this.userInput.addEventListener('input', () => {
            this.updateSendButton();
            this.autoResize();
        });
        
        // Microphone button
        this.micButton.addEventListener('click', () => this.toggleSpeechRecognition());
        
        // Focus input on page load
        this.userInput.focus();
        
        // Add voice control button
        this.addVoiceControlButton();
    }

    initializeSpeechRecognition() {
        if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            this.recognition = new SpeechRecognition();
            
            this.recognition.continuous = false;
            this.recognition.interimResults = false;
            this.recognition.lang = 'en-US';
            
            this.recognition.onstart = () => {
                this.isListening = true;
                this.micButton.classList.add('listening');
                this.updateStatus('Listening...', 'processing');
                this.stopSpeaking(); // Stop any current speech
            };
            
            this.recognition.onresult = (event) => {
                const transcript = event.results[0][0].transcript;
                this.userInput.value = transcript;
                this.updateSendButton();
                this.autoResize();
                this.sendMessage();
            };
            
            this.recognition.onerror = (event) => {
                console.error('Speech recognition error:', event.error);
                this.updateStatus('Speech error', 'error');
                setTimeout(() => this.updateStatus('Ready', 'ready'), 3000);
            };
            
            this.recognition.onend = () => {
                this.isListening = false;
                this.micButton.classList.remove('listening');
                if (this.statusText.textContent === 'Listening...') {
                    this.updateStatus('Ready', 'ready');
                }
            };
        } else {
            this.micButton.style.display = 'none';
        }
    }

    initializeTextToSpeech() {
        if ('speechSynthesis' in window) {
            // Wait for voices to load
            const loadVoices = () => {
                const voices = this.speechSynthesis.getVoices();
                // Prefer English voices, especially male voices for Jarvis
                const preferredVoices = voices.filter(voice => 
                    voice.lang.startsWith('en') && 
                    (voice.name.toLowerCase().includes('male') || 
                     voice.name.toLowerCase().includes('david') ||
                     voice.name.toLowerCase().includes('alex'))
                );
                
                if (preferredVoices.length > 0) {
                    this.preferredVoice = preferredVoices[0];
                } else {
                    // Fallback to any English voice
                    this.preferredVoice = voices.find(voice => voice.lang.startsWith('en')) || voices[0];
                }
            };

            if (this.speechSynthesis.getVoices().length > 0) {
                loadVoices();
            } else {
                this.speechSynthesis.onvoiceschanged = loadVoices;
            }
        }
    }

    addVoiceControlButton() {
        const headerActions = document.querySelector('.header-actions');
        const voiceButton = document.createElement('button');
        voiceButton.className = 'clear-btn voice-toggle-btn';
        voiceButton.innerHTML = `
            <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                <path d="M3,9V15H7L12,20V4L7,9H3M16.5,12C16.5,10.23 15.5,8.71 14,7.97V16.02C15.5,15.29 16.5,13.76 16.5,12M14,3.23V5.29C16.89,6.15 19,8.83 19,12C19,15.17 16.89,17.85 14,18.71V20.77C18.01,19.86 21,16.28 21,12C21,7.72 18.01,4.14 14,3.23Z"/>
            </svg>
            <span>Voice: ON</span>
        `;
        voiceButton.title = 'Toggle voice responses';
        voiceButton.onclick = () => this.toggleVoice();
        
        headerActions.insertBefore(voiceButton, headerActions.firstChild);
        this.voiceButton = voiceButton;
        this.voiceEnabled = true;
    }

    toggleVoice() {
        this.voiceEnabled = !this.voiceEnabled;
        const span = this.voiceButton.querySelector('span');
        span.textContent = this.voiceEnabled ? 'Voice: ON' : 'Voice: OFF';
        
        if (!this.voiceEnabled) {
            this.stopSpeaking();
        }
        
        // Save preference
        localStorage.setItem('jarvisVoiceEnabled', this.voiceEnabled);
    }

    speakText(text) {
        if (!this.voiceEnabled || !this.speechSynthesis || this.isSpeaking) {
            return;
        }

        // Clean text for speech (remove markdown, emojis, etc.)
        const cleanText = this.cleanTextForSpeech(text);
        
        if (!cleanText.trim()) return;

        this.currentUtterance = new SpeechSynthesisUtterance(cleanText);
        
        // Configure voice settings
        this.currentUtterance.rate = this.voiceSettings.rate;
        this.currentUtterance.pitch = this.voiceSettings.pitch;
        this.currentUtterance.volume = this.voiceSettings.volume;
        
        if (this.preferredVoice) {
            this.currentUtterance.voice = this.preferredVoice;
        }

        this.currentUtterance.onstart = () => {
            this.isSpeaking = true;
            this.updateStatus('Speaking...', 'processing');
        };

        this.currentUtterance.onend = () => {
            this.isSpeaking = false;
            this.currentUtterance = null;
            if (this.statusText.textContent === 'Speaking...') {
                this.updateStatus('Ready', 'ready');
            }
        };

        this.currentUtterance.onerror = (event) => {
            console.error('Speech synthesis error:', event.error);
            this.isSpeaking = false;
            this.currentUtterance = null;
        };

        this.speechSynthesis.speak(this.currentUtterance);
    }

    stopSpeaking() {
        if (this.speechSynthesis && this.isSpeaking) {
            this.speechSynthesis.cancel();
            this.isSpeaking = false;
            this.currentUtterance = null;
        }
    }

    cleanTextForSpeech(text) {
        return text
            // Remove markdown formatting
            .replace(/\*\*(.*?)\*\*/g, '$1')
            .replace(/\*(.*?)\*/g, '$1')
            .replace(/`(.*?)`/g, '$1')
            // Remove emojis and symbols
            .replace(/[\u{1F600}-\u{1F64F}]|[\u{1F300}-\u{1F5FF}]|[\u{1F680}-\u{1F6FF}]|[\u{1F1E0}-\u{1F1FF}]|[\u{2600}-\u{26FF}]|[\u{2700}-\u{27BF}]/gu, '')
            // Remove URLs
            .replace(/https?:\/\/[^\s]+/g, 'link')
            // Clean up extra spaces and newlines
            .replace(/\n+/g, '. ')
            .replace(/\s+/g, ' ')
            .trim();
    }

    toggleSpeechRecognition() {
        if (!this.recognition) return;
        
        if (this.isListening) {
            this.recognition.stop();
        } else {
            this.recognition.start();
        }
    }

    updateSendButton() {
        const hasText = this.userInput.value.trim().length > 0;
        this.sendButton.disabled = !hasText || this.isTyping;
    }

    autoResize() {
        this.userInput.style.height = 'auto';
        this.userInput.style.height = Math.min(this.userInput.scrollHeight, 200) + 'px';
    }

    async sendMessage() {
        const message = this.userInput.value.trim();
        if (!message || this.isTyping) return;
        
        // Stop any current speech
        this.stopSpeaking();
        
        // Add user message
        this.addMessage(message, 'user');
        this.userInput.value = '';
        this.autoResize();
        this.updateSendButton();
        
        // Show typing indicator
        this.showTypingIndicator();
        this.updateStatus('Thinking...', 'processing');
        
        try {
            const response = await fetch('/process_command', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ command: message })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            
            // Remove typing indicator
            this.hideTypingIndicator();
            
            // Handle special commands
            if (message.toLowerCase().includes('clear')) {
                this.clearChat();
                this.updateStatus('Ready', 'ready');
                return;
            }
            
            // Handle website opening
            if (data.response && data.response.includes('Opening')) {
                this.handleWebsiteOpen(message);
            }
            
            // Add assistant response with typing effect and speech
            const responseText = data.response || 'I received your message but got an empty response.';
            setTimeout(() => {
                this.typeMessage(responseText, 'assistant');
                this.updateStatus('Ready', 'ready');
                
                // Speak the response after a short delay
                setTimeout(() => {
                    this.speakText(responseText);
                }, 800);
            }, 300);
            
        } catch (error) {
            console.error('Error:', error);
            this.hideTypingIndicator();
            const errorMessage = 'Sorry, I encountered an error connecting to the server. Please make sure the Flask server is running and try again.';
            this.addMessage(errorMessage, 'assistant');
            this.speakText(errorMessage);
            this.updateStatus('Connection error', 'error');
            setTimeout(() => this.updateStatus('Ready', 'ready'), 3000);
        }
    }

    handleWebsiteOpen(message) {
        const websites = {
            'google': 'https://www.google.com',
            'youtube': 'https://www.youtube.com',
            'github': 'https://www.github.com',
            'stackoverflow': 'https://stackoverflow.com',
            'wikipedia': 'https://www.wikipedia.org',
            'reddit': 'https://www.reddit.com',
            'twitter': 'https://www.twitter.com',
            'facebook': 'https://www.facebook.com',
            'instagram': 'https://www.instagram.com',
            'linkedin': 'https://www.linkedin.com'
        };
        
        for (const [site, url] of Object.entries(websites)) {
            if (message.toLowerCase().includes(site)) {
                window.open(url, '_blank');
                break;
            }
        }
    }

    addMessage(content, sender, timestamp = null) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}-message`;
        
        const currentTime = timestamp || new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
        
        messageDiv.innerHTML = `
            <div class="message-header">
                <div class="message-avatar ${sender}-avatar">
                    ${sender === 'user' ? 'U' : 'J'}
                </div>
                <span class="message-sender">${sender === 'user' ? 'You' : 'Jarvis'}</span>
            </div>
            <div class="message-content">
                ${this.formatMessage(content)}
            </div>
            <div class="message-time">${currentTime}</div>
        `;
        
        this.chatMessages.appendChild(messageDiv);
        this.scrollToBottom();
        
        // Play sound effect
        if (typeof playSound === 'function') {
            playSound(sender === 'user' ? 'sendSound' : 'receiveSound');
        }
    }

    typeMessage(content, sender, timestamp = null) {
        this.isTyping = true;
        this.updateSendButton();
        
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}-message`;
        
        const currentTime = timestamp || new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
        
        messageDiv.innerHTML = `
            <div class="message-header">
                <div class="message-avatar ${sender}-avatar">
                    ${sender === 'user' ? 'U' : 'J'}
                </div>
                <span class="message-sender">${sender === 'user' ? 'You' : 'Jarvis'}</span>
            </div>
            <div class="message-content"></div>
            <div class="message-time">${currentTime}</div>
        `;
        
        this.chatMessages.appendChild(messageDiv);
        this.scrollToBottom();
        
        const contentElement = messageDiv.querySelector('.message-content');
        let index = 0;
        
        const typeInterval = setInterval(() => {
            if (index < content.length) {
                contentElement.textContent += content[index];
                index++;
                this.scrollToBottom();
            } else {
                clearInterval(typeInterval);
                // Format the final message
                contentElement.innerHTML = this.formatMessage(content);
                this.isTyping = false;
                this.updateSendButton();
                
                // Play receive sound when typing is complete
                if (typeof playSound === 'function') {
                    playSound('receiveSound');
                }
            }
        }, 20);
    }

    showTypingIndicator() {
        const typingDiv = document.createElement('div');
        typingDiv.className = 'message assistant-message typing-message';
        typingDiv.innerHTML = `
            <div class="message-header">
                <div class="message-avatar assistant-avatar">J</div>
                <span class="message-sender">Jarvis</span>
            </div>
            <div class="typing-indicator">
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
            </div>
        `;
        
        this.chatMessages.appendChild(typingDiv);
        this.scrollToBottom();
    }

    hideTypingIndicator() {
        const typingMessage = this.chatMessages.querySelector('.typing-message');
        if (typingMessage) {
            typingMessage.remove();
        }
    }

    formatMessage(content) {
        return content
            .replace(/\n/g, '<br>')
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/(https?:\/\/[^\s]+)/g, '<a href="$1" target="_blank" rel="noopener noreferrer">$1</a>');
    }

    clearChat() {
        this.stopSpeaking();
        this.chatMessages.innerHTML = '';
        setTimeout(() => {
            const clearMessage = "Chat cleared! How can I help you now?";
            this.addMessage(clearMessage, 'assistant');
            this.speakText(clearMessage);
        }, 100);
    }

    scrollToBottom() {
        this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
    }

    updateStatus(text, type) {
        this.statusText.textContent = text;
        this.statusDot.className = `status-dot ${type}`;
    }
}

// Quick command function
function sendQuickCommand(command) {
    const jarvisUI = window.jarvisUI;
    if (jarvisUI) {
        jarvisUI.userInput.value = command;
        jarvisUI.updateSendButton();
        jarvisUI.autoResize();
        jarvisUI.sendMessage();
    }
}

// Initialize Jarvis UI when page loads
document.addEventListener('DOMContentLoaded', () => {
    window.jarvisUI = new JarvisUI();
    
    // Load voice preference
    const voiceEnabled = localStorage.getItem('jarvisVoiceEnabled');
    if (voiceEnabled !== null) {
        window.jarvisUI.voiceEnabled = voiceEnabled === 'true';
        const span = window.jarvisUI.voiceButton?.querySelector('span');
        if (span) {
            span.textContent = window.jarvisUI.voiceEnabled ? 'Voice: ON' : 'Voice: OFF';
        }
    }
});

// Connection status checker
function checkServerConnection() {
    fetch('/process_command', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ command: 'ping' })
    })
    .then(response => {
        if (response.ok && window.jarvisUI) {
            window.jarvisUI.updateStatus('Ready', 'ready');
        }
    })
    .catch(error => {
        console.error('Server connection check failed:', error);
        if (window.jarvisUI) {
            window.jarvisUI.updateStatus('Server offline', 'error');
        }
    });
}

// Check server connection every 30 seconds
setInterval(checkServerConnection, 30000);