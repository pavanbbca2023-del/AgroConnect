/**
 * Session Management for Concurrent Login Support
 * Handles multiple active sessions for AgroConnect users
 */

class SessionManager {
    constructor() {
        this.refreshInterval = 30000; // 30 seconds
        this.intervalId = null;
        this.init();
    }

    init() {
        if (this.isUserLoggedIn()) {
            this.startSessionMonitoring();
            this.bindEvents();
        }
    }

    isUserLoggedIn() {
        // Check if user is logged in (you can customize this check)
        return document.body.classList.contains('logged-in') || 
               document.querySelector('[data-user-id]') !== null;
    }

    startSessionMonitoring() {
        this.refreshSessions();
        this.intervalId = setInterval(() => {
            this.refreshSessions();
        }, this.refreshInterval);
    }

    stopSessionMonitoring() {
        if (this.intervalId) {
            clearInterval(this.intervalId);
            this.intervalId = null;
        }
    }

    async refreshSessions() {
        try {
            const response = await fetch('/api/sessions/', {
                method: 'GET',
                headers: {
                    'X-CSRFToken': this.getCSRFToken(),
                    'Content-Type': 'application/json',
                },
                credentials: 'same-origin'
            });

            if (response.ok) {
                const data = await response.json();
                this.updateSessionDisplay(data);
            }
        } catch (error) {
            console.warn('Failed to refresh session data:', error);
        }
    }

    async terminateSession(sessionKey) {
        try {
            const response = await fetch('/api/sessions/terminate/', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': this.getCSRFToken(),
                    'Content-Type': 'application/json',
                },
                credentials: 'same-origin',
                body: JSON.stringify({ session_key: sessionKey })
            });

            const data = await response.json();
            
            if (data.success) {
                this.showMessage('Session terminated successfully', 'success');
                this.refreshSessions();
            } else {
                this.showMessage(data.error || 'Failed to terminate session', 'error');
            }
        } catch (error) {
            this.showMessage('Network error occurred', 'error');
        }
    }

    updateSessionDisplay(data) {
        const container = document.getElementById('active-sessions');
        if (!container) return;

        if (data.success && data.sessions) {
            const sessionsHtml = data.sessions.map(session => `
                <div class="session-item ${session.is_current ? 'current-session' : ''}" data-session="${session.session_id}">
                    <div class="session-info">
                        <span class="session-id">Session: ${session.session_id}</span>
                        <span class="login-time">Login: ${new Date(session.login_time).toLocaleString()}</span>
                        ${session.is_current ? '<span class="current-badge">Current</span>' : ''}
                    </div>
                    ${!session.is_current ? `
                        <button class="btn btn-sm btn-outline-danger terminate-session" 
                                data-session-key="${session.session_key}">
                            Terminate
                        </button>
                    ` : ''}
                </div>
            `).join('');

            container.innerHTML = `
                <div class="sessions-header">
                    <h6>Active Sessions (${data.total_sessions})</h6>
                    <small class="text-muted">You can be logged in from multiple devices</small>
                </div>
                <div class="sessions-list">
                    ${sessionsHtml}
                </div>
            `;

            // Bind terminate buttons
            container.querySelectorAll('.terminate-session').forEach(btn => {
                btn.addEventListener('click', (e) => {
                    const sessionKey = e.target.dataset.sessionKey;
                    if (confirm('Are you sure you want to terminate this session?')) {
                        this.terminateSession(sessionKey);
                    }
                });
            });
        }
    }

    bindEvents() {
        // Handle page visibility changes
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                this.stopSessionMonitoring();
            } else {
                this.startSessionMonitoring();
            }
        });

        // Handle window beforeunload
        window.addEventListener('beforeunload', () => {
            this.stopSessionMonitoring();
        });
    }

    getCSRFToken() {
        const token = document.querySelector('[name=csrfmiddlewaretoken]');
        return token ? token.value : '';
    }

    showMessage(message, type = 'info') {
        // Create or update message display
        let messageContainer = document.getElementById('session-messages');
        if (!messageContainer) {
            messageContainer = document.createElement('div');
            messageContainer.id = 'session-messages';
            messageContainer.className = 'position-fixed top-0 end-0 p-3';
            messageContainer.style.zIndex = '1050';
            document.body.appendChild(messageContainer);
        }

        const alertClass = type === 'success' ? 'alert-success' : 
                          type === 'error' ? 'alert-danger' : 'alert-info';

        const alertHtml = `
            <div class="alert ${alertClass} alert-dismissible fade show" role="alert">
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `;

        messageContainer.insertAdjacentHTML('beforeend', alertHtml);

        // Auto-remove after 5 seconds
        setTimeout(() => {
            const alerts = messageContainer.querySelectorAll('.alert');
            if (alerts.length > 0) {
                alerts[0].remove();
            }
        }, 5000);
    }
}

// Initialize session manager when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.sessionManager = new SessionManager();
});

// Export for use in other scripts
window.SessionManager = SessionManager;