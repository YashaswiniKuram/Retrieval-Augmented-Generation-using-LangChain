// RAG Chat Assistant Frontend JavaScript

class RAGChatApp {
    constructor() {
        this.apiBase = '/api';
        this.chatHistory = [];
        this.isProcessing = false;
        this.init();
    }

    init() {
        this.loadChatHistory();
        this.setupEventListeners();
        this.checkConnection();
        this.loadDocuments();
        this.autoResizeTextarea();
    }

    setupEventListeners() {
        // File upload events
        const fileInput = document.getElementById('file-input');
        const uploadArea = document.getElementById('upload-area');
        const chatInput = document.getElementById('chat-input');
        const sendBtn = document.getElementById('send-btn');

        fileInput.addEventListener('change', (e) => this.handleFileSelect(e));
        
        // Drag and drop events
        uploadArea.addEventListener('dragover', (e) => this.handleDragOver(e));
        uploadArea.addEventListener('dragleave', (e) => this.handleDragLeave(e));
        uploadArea.addEventListener('drop', (e) => this.handleDrop(e));
        
        // Chat input events
        chatInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });

        chatInput.addEventListener('input', () => this.autoResizeTextarea());
        
        // Send button
        sendBtn.addEventListener('click', () => this.sendMessage());
    }

    async checkConnection() {
        try {
            const response = await fetch(`${this.apiBase}/health`);
            const data = await response.json();
            
            const statusDot = document.getElementById('status-dot');
            const statusText = document.getElementById('status-text');
            
            if (data.status === 'healthy') {
                statusDot.classList.remove('offline');
                statusText.textContent = 'Connected';
            } else {
                statusDot.classList.add('offline');
                statusText.textContent = 'Connection issues';
            }
        } catch (error) {
            const statusDot = document.getElementById('status-dot');
            const statusText = document.getElementById('status-text');
            statusDot.classList.add('offline');
            statusText.textContent = 'Offline';
        }
    }

    async loadDocuments() {
        try {
            const response = await fetch(`${this.apiBase}/documents`);
            const data = await response.json();
            this.updateDocumentList(data.documents);
        } catch (error) {
            console.error('Error loading documents:', error);
        }
    }

    updateDocumentList(documents) {
        const documentList = document.getElementById('document-list');
        
        if (!documents || documents.length === 0) {
            documentList.innerHTML = '<p style="text-align: center; color: #999; padding: 20px;">No documents uploaded yet</p>';
            return;
        }

        documentList.innerHTML = documents.map(doc => `
            <div class="document-item">
                <div class="document-icon ${doc.type}">${doc.type.toUpperCase()}</div>
                <div class="document-info">
                    <div class="document-name">${doc.filename}</div>
                    <div class="document-size">${doc.size_mb} MB</div>
                </div>
            </div>
        `).join('');
    }

    handleFileSelect(event) {
        const files = Array.from(event.target.files);
        this.uploadFiles(files);
    }

    handleDragOver(event) {
        event.preventDefault();
        event.currentTarget.classList.add('dragover');
    }

    handleDragLeave(event) {
        event.currentTarget.classList.remove('dragover');
    }

    handleDrop(event) {
        event.preventDefault();
        event.currentTarget.classList.remove('dragover');
        
        const files = Array.from(event.dataTransfer.files);
        this.uploadFiles(files);
    }

    async uploadFiles(files) {
        const uploadBtn = document.getElementById('upload-btn');
        const originalText = uploadBtn.innerHTML;
        
        uploadBtn.disabled = true;
        uploadBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Uploading...';
        
        try {
            for (const file of files) {
                if (!this.isValidFileType(file)) {
                    this.showNotification(`Invalid file type: ${file.name}. Supported: PDF, DOC, DOCX, TXT`, 'error');
                    continue;
                }
                
                await this.uploadSingleFile(file);
            }
            
            // Reload documents list
            await this.loadDocuments();
            
            // Add system message about new documents
            this.addMessage('assistant', `I've processed ${files.length} new document(s). You can now ask me questions about them!`);
            
        } catch (error) {
            console.error('Upload error:', error);
            this.showNotification('Error uploading files', 'error');
        } finally {
            uploadBtn.disabled = false;
            uploadBtn.innerHTML = originalText;
        }
    }

    isValidFileType(file) {
        const allowedTypes = ['.pdf', '.doc', '.docx', '.txt'];
        const fileName = file.name.toLowerCase();
        return allowedTypes.some(type => fileName.endsWith(type));
    }

    async uploadSingleFile(file) {
        const formData = new FormData();
        formData.append('file', file);
        
        const response = await fetch(`${this.apiBase}/upload`, {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Upload failed');
        }
        
        const result = await response.json();
        this.showNotification(`Uploaded: ${file.name}`, 'success');
        
        return result;
    }

    async sendMessage() {
        const chatInput = document.getElementById('chat-input');
        const message = chatInput.value.trim();
        
        if (!message || this.isProcessing) return;
        
        // Add user message to chat
        this.addMessage('user', message);
        chatInput.value = '';
        this.autoResizeTextarea();
        
        // Show typing indicator
        this.showTypingIndicator();
        
        this.isProcessing = true;
        
        try {
            const response = await fetch(`${this.apiBase}/ask`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ question: message })
            });
            
            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.error || 'Failed to get response');
            }
            
            const data = await response.json();
            
            // Remove typing indicator
            this.removeTypingIndicator();
            
            // Add AI response
            this.addMessage('assistant', data.answer, data.sources);
            
        } catch (error) {
            console.error('Error sending message:', error);
            this.removeTypingIndicator();
            this.addMessage('assistant', `Sorry, I encountered an error: ${error.message}`, []);
        } finally {
            this.isProcessing = false;
        }
    }

    addMessage(sender, content, sources = []) {
        const chatMessages = document.getElementById('chat-messages');
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}`;
        
        const avatar = sender === 'user' ? 
            '<i class="fas fa-user"></i>' : 
            '<i class="fas fa-robot"></i>';
        
        const sourcesHtml = sources.length > 0 ? 
            `<div class="message-sources">Sources: ${sources.join(', ')}</div>` : '';
        
        messageDiv.innerHTML = `
            <div class="message-avatar">
                ${avatar}
            </div>
            <div class="message-content">
                <div class="message-text">${content}</div>
                ${sourcesHtml}
            </div>
        `;
        
        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
        
        // Save to chat history
        this.chatHistory.push({
            sender,
            content,
            sources,
            timestamp: new Date().toISOString()
        });
        
        this.saveChatHistory();
    }

    showTypingIndicator() {
        const chatMessages = document.getElementById('chat-messages');
        const typingDiv = document.createElement('div');
        typingDiv.className = 'typing-indicator';
        typingDiv.id = 'typing-indicator';
        typingDiv.innerHTML = `
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
        `;
        
        chatMessages.appendChild(typingDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    removeTypingIndicator() {
        const typingIndicator = document.getElementById('typing-indicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }
    }

    autoResizeTextarea() {
        const chatInput = document.getElementById('chat-input');
        chatInput.style.height = 'auto';
        chatInput.style.height = Math.min(chatInput.scrollHeight, 120) + 'px';
    }

    loadChatHistory() {
        try {
            const saved = localStorage.getItem('ragChatHistory');
            if (saved) {
                this.chatHistory = JSON.parse(saved);
                this.displayChatHistory();
            }
        } catch (error) {
            console.error('Error loading chat history:', error);
        }
    }

    displayChatHistory() {
        const chatMessages = document.getElementById('chat-messages');
        
        // Clear existing messages except the welcome message
        const welcomeMessage = chatMessages.querySelector('.message.assistant');
        chatMessages.innerHTML = '';
        if (welcomeMessage) {
            chatMessages.appendChild(welcomeMessage);
        }
        
        // Add saved messages
        this.chatHistory.forEach(msg => {
            this.addMessage(msg.sender, msg.content, msg.sources);
        });
    }

    saveChatHistory() {
        try {
            localStorage.setItem('ragChatHistory', JSON.stringify(this.chatHistory));
        } catch (error) {
            console.error('Error saving chat history:', error);
        }
    }

    clearChat() {
        this.chatHistory = [];
        this.saveChatHistory();
        
        const chatMessages = document.getElementById('chat-messages');
        chatMessages.innerHTML = `
            <div class="message assistant">
                <div class="message-avatar">
                    <i class="fas fa-robot"></i>
                </div>
                <div class="message-content">
                    <div class="message-text">
                        Chat history cleared. How can I help you today?
                    </div>
                </div>
            </div>
        `;
        
        this.showNotification('Chat history cleared', 'success');
    }

    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 15px 20px;
            border-radius: 10px;
            color: white;
            font-weight: 500;
            z-index: 1000;
            animation: slideIn 0.3s ease;
            max-width: 300px;
            word-wrap: break-word;
        `;
        
        // Set background color based on type
        switch (type) {
            case 'success':
                notification.style.background = '#28a745';
                break;
            case 'error':
                notification.style.background = '#dc3545';
                break;
            case 'warning':
                notification.style.background = '#ffc107';
                notification.style.color = '#333';
                break;
            default:
                notification.style.background = '#17a2b8';
        }
        
        notification.textContent = message;
        document.body.appendChild(notification);
        
        // Remove notification after 3 seconds
        setTimeout(() => {
            notification.style.animation = 'slideOut 0.3s ease';
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            }, 300);
        }, 3000);
    }
}

// Add CSS animations for notifications
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    
    @keyframes slideOut {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(100%); opacity: 0; }
    }
`;
document.head.appendChild(style);

// Global functions for HTML onclick events
function sendMessage() {
    if (window.ragApp) {
        window.ragApp.sendMessage();
    }
}

function clearChat() {
    if (window.ragApp) {
        window.ragApp.clearChat();
    }
}

// Initialize the app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.ragApp = new RAGChatApp();
}); 