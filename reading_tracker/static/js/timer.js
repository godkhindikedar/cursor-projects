// Enhanced Timer functionality for study sessions - No Flickering!
class StudyTimer {
    constructor() {
        this.interval = null;
        this.startTime = null;
        this.isRunning = false;
        this.lastDisplay = '';
        this.element = null;
        this.animationFrame = null;
    }

    start(startTime = new Date()) {
        // Stop any existing timer first to prevent conflicts
        this.stop();
        
        this.startTime = startTime;
        this.isRunning = true;
        this.element = document.getElementById('timer-display');
        this.lastDisplay = '';
        
        if (this.element) {
            // Clear any existing timers on the page to prevent conflicts
            this.clearPageTimers();
            
            // Update immediately for smooth start
            this.updateDisplay();
            
            // Use a precise interval that prevents drift
            this.interval = setInterval(() => {
                this.updateDisplay();
            }, 1000);
        }
    }

    stop() {
        if (this.interval) {
            clearInterval(this.interval);
            this.interval = null;
        }
        if (this.animationFrame) {
            cancelAnimationFrame(this.animationFrame);
            this.animationFrame = null;
        }
        this.isRunning = false;
        this.element = null;
        this.lastDisplay = '';
    }

    updateDisplay() {
        if (!this.startTime || !this.element) return;

        const now = new Date();
        const elapsed = Math.max(0, Math.floor((now - this.startTime) / 1000));
        
        const hours = Math.floor(elapsed / 3600);
        const minutes = Math.floor((elapsed % 3600) / 60);
        const seconds = elapsed % 60;
        
        const display = `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
        
        // Only update DOM if the display has actually changed (prevents flickering)
        if (display !== this.lastDisplay) {
            // Use requestAnimationFrame for smoother updates
            if (this.animationFrame) {
                cancelAnimationFrame(this.animationFrame);
            }
            
            this.animationFrame = requestAnimationFrame(() => {
                if (this.element) {
                    this.element.textContent = display;
                    this.lastDisplay = display;
                    
                    // Add smooth pulsing effect every minute (but not on first load)
                    if (elapsed > 0 && seconds === 0 && (minutes > 0 || hours > 0)) {
                        this.element.classList.add('animate-success');
                        setTimeout(() => {
                            if (this.element) {
                                this.element.classList.remove('animate-success');
                            }
                        }, 600);
                    }
                }
            });
        }
    }

    getElapsedMinutes() {
        if (!this.startTime) return 0;
        const now = new Date();
        return Math.floor((now - this.startTime) / 60000);
    }

    // Check if timer is currently active
    isActive() {
        return this.isRunning && this.interval !== null;
    }

    // Clear any other timer intervals on the page to prevent conflicts
    clearPageTimers() {
        // Clear any global timerInterval variables that might exist
        if (window.timerInterval) {
            clearInterval(window.timerInterval);
            window.timerInterval = null;
        }
        
        // Stop any other StudyTimer instances
        if (window.studyTimer && window.studyTimer !== this) {
            window.studyTimer.stop();
        }
    }
}

// Global timer instance
const studyTimer = new StudyTimer();

// Check for active session on page load
document.addEventListener('DOMContentLoaded', function() {
    checkActiveSession();
    
    // Add click handlers for study buttons
    const studyButtons = document.querySelectorAll('[data-subject]');
    studyButtons.forEach(button => {
        button.addEventListener('click', function() {
            const subject = this.getAttribute('data-subject');
            startStudySession(subject);
        });
    });
});

// Check if there's an active study session
function checkActiveSession() {
    fetch('/study/current')
        .then(response => response.json())
        .then(data => {
            if (data.active) {
                const startTime = new Date(data.start_time);
                studyTimer.start(startTime);
                
                // Show active session UI if elements exist
                showActiveSessionUI(data.subject, data.elapsed_seconds);
            }
        })
        .catch(error => {
            console.log('No active session check endpoint available');
        });
}

// Show active session UI elements
function showActiveSessionUI(subject, elapsedSeconds) {
    // This function can be customized based on the page
    const activeSessionElements = document.querySelectorAll('.active-session');
    activeSessionElements.forEach(element => {
        element.style.display = 'block';
    });
}

// Start a new study session
function startStudySession(subject) {
    const formData = new FormData();
    formData.append('subject', subject);
    
    // Send browser's current time to server
    const now = new Date();
    formData.append('start_time', now.toISOString());
    
    // Show loading state
    const startButton = document.querySelector(`[data-subject="${subject}"]`);
    if (startButton) {
        const originalText = startButton.innerHTML;
        startButton.innerHTML = '<span class="loading"></span> Starting...';
        startButton.disabled = true;
        
        setTimeout(() => {
            startButton.innerHTML = originalText;
            startButton.disabled = false;
        }, 2000);
    }
    
    fetch('/study/start', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Start the timer
            studyTimer.start();
            
            // Show success message with special message for reading
            const subjectName = subject.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase());
            let message = `Started studying ${subjectName}!`;
            let icon = '📚';
            
            if (subject === 'reading') {
                message = `Time to dive into a great book! Happy Reading! 📖`;
                icon = '📖';
            } else if (subject === 'maths') {
                icon = '🔢';
            } else if (subject === 'science') {
                icon = '🧪';
            } else if (subject === 'writing') {
                icon = '✏️';
            } else if (subject === 'english') {
                icon = '🗣️';
            } else if (subject === 'social_studies') {
                icon = '🌍';
            }
            
            showNotification(`${icon} ${message}`, 'success');
            
            // Refresh page after a short delay to show active session
            setTimeout(() => {
                location.reload();
            }, 1500);
        } else {
            showNotification('Failed to start study session', 'error');
        }
    })
    .catch(error => {
        console.error('Error starting study session:', error);
        showNotification('Failed to start study session', 'error');
    });
}

// Stop the current study session
function stopStudySession(notes = '') {
    const formData = new FormData();
    if (notes) {
        formData.append('notes', notes);
    }
    
    // Send browser's current time to server
    const now = new Date();
    formData.append('end_time', now.toISOString());
    
    fetch('/study/stop', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            studyTimer.stop();
            
            // Show completion message with duration
            const duration = data.duration || studyTimer.getElapsedMinutes();
            showNotification(`Great job! You studied for ${duration} minutes!`, 'success');
            
            // Refresh page after showing message
            setTimeout(() => {
                location.reload();
            }, 2000);
        } else {
            showNotification('Failed to stop study session', 'error');
        }
    })
    .catch(error => {
        console.error('Error stopping study session:', error);
        showNotification('Failed to stop study session', 'error');
    });
}

// Show notification messages
function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `alert alert-${type === 'error' ? 'danger' : type === 'success' ? 'success' : 'info'} position-fixed`;
    notification.style.cssText = `
        top: 20px;
        right: 20px;
        z-index: 9999;
        min-width: 300px;
        opacity: 0;
        transform: translateX(100%);
        transition: all 0.3s ease;
    `;
    
    notification.innerHTML = `
        <div class="d-flex align-items-center">
            <i class="fas fa-${type === 'error' ? 'exclamation-circle' : type === 'success' ? 'check-circle' : 'info-circle'} me-2"></i>
            <span>${message}</span>
            <button type="button" class="btn-close ms-auto" onclick="this.parentElement.parentElement.remove()"></button>
        </div>
    `;
    
    document.body.appendChild(notification);
    
    // Animate in
    setTimeout(() => {
        notification.style.opacity = '1';
        notification.style.transform = 'translateX(0)';
    }, 100);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        notification.style.opacity = '0';
        notification.style.transform = 'translateX(100%)';
        setTimeout(() => {
            if (notification.parentElement) {
                notification.remove();
            }
        }, 300);
    }, 5000);
}

// Format time duration for display
function formatDuration(seconds) {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    
    if (hours > 0) {
        return `${hours}h ${minutes}m ${secs}s`;
    } else if (minutes > 0) {
        return `${minutes}m ${secs}s`;
    } else {
        return `${secs}s`;
    }
}

// Convert UTC time to CST (Central Standard Time)
function formatCSTDateTime(utcDateString) {
    try {
        const date = new Date(utcDateString);
        // CST is UTC-6, CDT is UTC-5. We'll use CST (UTC-6) as requested
        const cstOffset = -6 * 60; // -6 hours in minutes
        const cstDate = new Date(date.getTime() + (cstOffset * 60 * 1000));
        
        return cstDate.toLocaleString('en-US', {
            timeZone: 'America/Chicago',
            year: 'numeric',
            month: 'long',
            day: 'numeric',
            hour: 'numeric',
            minute: '2-digit',
            hour12: true
        }) + ' CST';
    } catch (e) {
        return utcDateString;
    }
}

// Convert UTC time to CST date only
function formatCSTDate(utcDateString) {
    try {
        const date = new Date(utcDateString);
        return date.toLocaleDateString('en-US', {
            timeZone: 'America/Chicago',
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });
    } catch (e) {
        return utcDateString;
    }
}

// Convert UTC time to CST time only
function formatCSTTime(utcDateString) {
    try {
        const date = new Date(utcDateString);
        return date.toLocaleTimeString('en-US', {
            timeZone: 'America/Chicago',
            hour: 'numeric',
            minute: '2-digit',
            hour12: true
        }) + ' CST';
    } catch (e) {
        return utcDateString;
    }
}

// Format datetime in user's local timezone (keeping for backward compatibility)
function formatLocalDateTime(utcDateString) {
    try {
        const date = new Date(utcDateString);
        return date.toLocaleString();
    } catch (e) {
        return utcDateString;
    }
}

// Format date in user's local timezone (date only)
function formatLocalDate(utcDateString) {
    try {
        const date = new Date(utcDateString);
        return date.toLocaleDateString();
    } catch (e) {
        return utcDateString;
    }
}

// Format time in user's local timezone (time only)
function formatLocalTime(utcDateString) {
    try {
        const date = new Date(utcDateString);
        return date.toLocaleTimeString();
    } catch (e) {
        return utcDateString;
    }
}

// Add motivational messages for different durations
function getMotivationalMessage(minutes) {
    if (minutes >= 60) {
        return "Wow! You're a study champion! 🏆";
    } else if (minutes >= 30) {
        return "Amazing focus! You're doing great! ⭐";
    } else if (minutes >= 15) {
        return "Good job! Keep up the great work! 👏";
    } else if (minutes >= 5) {
        return "Nice start! Every minute counts! 🌟";
    } else {
        return "Great beginning! 🚀";
    }
}

// Convert all UTC timestamps to CST time on page load
document.addEventListener('DOMContentLoaded', function() {
    // Find all elements with UTC timestamps and convert them to CST
    const timestampElements = document.querySelectorAll('[data-utc-time]');
    timestampElements.forEach(element => {
        const utcTime = element.getAttribute('data-utc-time');
        const format = element.getAttribute('data-time-format') || 'datetime';
        
        if (format === 'date') {
            element.textContent = formatCSTDate(utcTime);
        } else if (format === 'time') {
            element.textContent = formatCSTTime(utcTime);
        } else {
            element.textContent = formatCSTDateTime(utcTime);
        }
    });
    
    // Also convert any Recent Study Sessions times that don't use data-utc-time
    const recentSessionTimes = document.querySelectorAll('.recent-session-time');
    recentSessionTimes.forEach(element => {
        const utcTime = element.getAttribute('data-utc');
        if (utcTime) {
            element.textContent = formatCSTDateTime(utcTime);
        }
    });
});

// Export functions for use in other scripts
window.StudyTimer = {
    start: startStudySession,
    stop: stopStudySession,
    timer: studyTimer,
    showNotification: showNotification,
    formatDuration: formatDuration,
    formatCSTDateTime: formatCSTDateTime,
    formatCSTDate: formatCSTDate,
    formatCSTTime: formatCSTTime,
    formatLocalDateTime: formatLocalDateTime,
    formatLocalDate: formatLocalDate,
    formatLocalTime: formatLocalTime,
    getMotivationalMessage: getMotivationalMessage
};