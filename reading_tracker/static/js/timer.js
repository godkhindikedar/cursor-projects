// Timer functionality for study sessions
class StudyTimer {
    constructor() {
        this.interval = null;
        this.startTime = null;
        this.isRunning = false;
    }

    start(startTime = new Date()) {
        this.startTime = startTime;
        this.isRunning = true;
        this.updateDisplay();
        this.interval = setInterval(() => this.updateDisplay(), 1000);
    }

    stop() {
        if (this.interval) {
            clearInterval(this.interval);
            this.interval = null;
        }
        this.isRunning = false;
    }

    updateDisplay() {
        if (!this.startTime) return;

        const now = new Date();
        const elapsed = Math.floor((now - this.startTime) / 1000);
        
        const hours = Math.floor(elapsed / 3600);
        const minutes = Math.floor((elapsed % 3600) / 60);
        const seconds = elapsed % 60;
        
        const display = `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
        
        const timerElement = document.getElementById('timer-display');
        if (timerElement) {
            timerElement.textContent = display;
            
            // Add pulsing effect every minute
            if (seconds === 0 && (minutes > 0 || hours > 0)) {
                timerElement.classList.add('animate-success');
                setTimeout(() => {
                    timerElement.classList.remove('animate-success');
                }, 600);
            }
        }
    }

    getElapsedMinutes() {
        if (!this.startTime) return 0;
        const now = new Date();
        return Math.floor((now - this.startTime) / 60000);
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
            
            // Show success message
            showNotification(`Started studying ${subject.replace('_', ' ')}!`, 'success');
            
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

// Export functions for use in other scripts
window.StudyTimer = {
    start: startStudySession,
    stop: stopStudySession,
    timer: studyTimer,
    showNotification: showNotification,
    formatDuration: formatDuration,
    getMotivationalMessage: getMotivationalMessage
};
