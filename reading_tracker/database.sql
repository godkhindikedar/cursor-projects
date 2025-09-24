-- Reading & Study Tracker Database Schema
-- Create the database
CREATE DATABASE IF NOT EXISTS reading_tracker;
USE reading_tracker;

-- Users table for storing Google OAuth user information
CREATE TABLE user (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(100) NOT NULL UNIQUE,
    name VARCHAR(100) NOT NULL,
    google_id VARCHAR(100) NOT NULL UNIQUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_email (email),
    INDEX idx_google_id (google_id)
);

-- Books table for tracking reading
CREATE TABLE book (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    author VARCHAR(100),
    summary TEXT,
    date_read DATETIME DEFAULT CURRENT_TIMESTAMP,
    user_id INT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_date_read (date_read),
    INDEX idx_title (title)
);

-- Study sessions table for time tracking
CREATE TABLE study_session (
    id INT AUTO_INCREMENT PRIMARY KEY,
    subject ENUM('maths', 'writing', 'english', 'science', 'social_studies') NOT NULL,
    start_time DATETIME NOT NULL,
    end_time DATETIME,
    duration_minutes INT,
    notes TEXT,
    user_id INT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_subject (subject),
    INDEX idx_start_time (start_time),
    INDEX idx_duration (duration_minutes)
);

-- Insert sample data for testing (optional)
-- You can uncomment these lines for testing purposes

/*
-- Sample user (you'll need to replace with real Google OAuth data)
INSERT INTO user (email, name, google_id) VALUES 
('test@example.com', 'Test Student', 'google_test_id_123');

-- Sample books
INSERT INTO book (title, author, summary, user_id) VALUES 
('The Cat in the Hat', 'Dr. Seuss', 'A fun story about a cat who visits two children on a rainy day. I loved how the cat made the day exciting!', 1),
('Charlotte\'s Web', 'E.B. White', 'A beautiful story about friendship between a pig named Wilbur and a spider named Charlotte. It made me cry happy tears!', 1),
('Where the Wild Things Are', 'Maurice Sendak', 'Max goes on an amazing adventure to where the wild things live. The monsters were scary but friendly!', 1);

-- Sample study sessions
INSERT INTO study_session (subject, start_time, end_time, duration_minutes, notes, user_id) VALUES 
('maths', '2024-01-15 14:00:00', '2024-01-15 14:30:00', 30, 'Practiced multiplication tables. Getting faster!', 1),
('english', '2024-01-15 15:00:00', '2024-01-15 15:45:00', 45, 'Read a chapter from my book and wrote a summary.', 1),
('science', '2024-01-16 10:00:00', '2024-01-16 10:25:00', 25, 'Learned about the solar system. Jupiter is huge!', 1),
('writing', '2024-01-16 16:00:00', '2024-01-16 16:20:00', 20, 'Wrote a story about my pet dog.', 1);
*/

-- Create indexes for better performance
CREATE INDEX idx_book_user_date ON book(user_id, date_read DESC);
CREATE INDEX idx_session_user_start ON study_session(user_id, start_time DESC);
CREATE INDEX idx_session_subject_user ON study_session(subject, user_id);

-- Views for common queries

-- View for user statistics
CREATE VIEW user_stats AS
SELECT 
    u.id,
    u.name,
    u.email,
    COUNT(DISTINCT b.id) as total_books,
    COUNT(DISTINCT s.id) as total_sessions,
    COALESCE(SUM(s.duration_minutes), 0) as total_study_minutes,
    COALESCE(AVG(s.duration_minutes), 0) as avg_session_minutes
FROM user u
LEFT JOIN book b ON u.id = b.user_id
LEFT JOIN study_session s ON u.id = s.user_id AND s.end_time IS NOT NULL
GROUP BY u.id, u.name, u.email;

-- View for subject statistics
CREATE VIEW subject_stats AS
SELECT 
    u.id as user_id,
    u.name as user_name,
    s.subject,
    COUNT(s.id) as session_count,
    SUM(s.duration_minutes) as total_minutes,
    AVG(s.duration_minutes) as avg_minutes,
    MAX(s.start_time) as last_session
FROM user u
LEFT JOIN study_session s ON u.id = s.user_id AND s.end_time IS NOT NULL
WHERE s.subject IS NOT NULL
GROUP BY u.id, u.name, s.subject;

-- View for recent activity
CREATE VIEW recent_activity AS
SELECT 
    'book' as activity_type,
    b.id as item_id,
    b.title as item_title,
    b.author as item_subtitle,
    b.date_read as activity_date,
    b.user_id
FROM book b
UNION ALL
SELECT 
    'study' as activity_type,
    s.id as item_id,
    s.subject as item_title,
    CONCAT(s.duration_minutes, ' minutes') as item_subtitle,
    s.start_time as activity_date,
    s.user_id
FROM study_session s
WHERE s.end_time IS NOT NULL
ORDER BY activity_date DESC;

-- Triggers for data validation and automatic calculations

DELIMITER //

-- Trigger to automatically calculate duration when study session ends
CREATE TRIGGER calculate_duration 
BEFORE UPDATE ON study_session 
FOR EACH ROW
BEGIN
    IF NEW.end_time IS NOT NULL AND OLD.end_time IS NULL THEN
        SET NEW.duration_minutes = TIMESTAMPDIFF(MINUTE, NEW.start_time, NEW.end_time);
    END IF;
END//

-- Trigger to validate study session times
CREATE TRIGGER validate_study_session
BEFORE INSERT ON study_session
FOR EACH ROW
BEGIN
    IF NEW.end_time IS NOT NULL AND NEW.end_time <= NEW.start_time THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'End time must be after start time';
    END IF;
    
    IF NEW.start_time > NOW() THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Start time cannot be in the future';
    END IF;
END//

DELIMITER ;

-- Grant permissions (adjust username and password as needed)
-- CREATE USER 'reading_app'@'localhost' IDENTIFIED BY 'secure_password_here';
-- GRANT SELECT, INSERT, UPDATE, DELETE ON reading_tracker.* TO 'reading_app'@'localhost';
-- FLUSH PRIVILEGES;
