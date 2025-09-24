# 📚 Reading & Study Tracker

A kid-friendly web application to track reading books and study time across different subjects. Built with Python Flask, MySQL, and designed with a colorful, engaging interface perfect for children.

## ✨ Features

- **Book Tracking**: Log books with titles, authors, and personal summaries
- **Study Timer**: Start/stop timer for study sessions across 5 subjects
- **Subject Categories**: Maths, English, Science, Writing, Social Studies
- **Kid-Friendly Design**: Colorful, intuitive interface with emojis and animations
- **Google Authentication**: Secure login using Gmail accounts
- **Progress Tracking**: View study statistics and reading history
- **Real-time Timer**: Live timer display during study sessions

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- MySQL 8.0+
- Google Cloud Console account (for OAuth)

### 1. Installation

```bash
# Clone or download the project
cd reading_tracker

# Install dependencies
pip install -r requirements.txt
```

### 2. Database Setup

```bash
# Login to MySQL
mysql -u root -p

# Run the database schema
mysql -u root -p < database.sql
```

### 3. Google OAuth Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project or select existing one
3. Enable Google+ API
4. Create OAuth 2.0 credentials
5. Add authorized redirect URIs:
   - `http://localhost:5000`
   - `http://127.0.0.1:5000`

### 4. Environment Configuration

Create a `.env` file in the project root:

```env
SECRET_KEY=your-super-secret-key-here
DATABASE_URL=mysql+pymysql://username:password@localhost/reading_tracker
GOOGLE_CLIENT_ID=your-google-client-id.apps.googleusercontent.com
```

### 5. Run the Application

```bash
python app.py
```

Visit `http://localhost:5000` in your browser!

## 🎨 Screenshots

### Dashboard
- Welcome message with child's name
- Quick action cards for adding books and starting study sessions
- Recent activity overview
- Active study session timer

### Book Tracking
- Add new books with title, author, and personal summary
- View reading library with colorful book cards
- Reading statistics and progress

### Study Sessions
- Subject selection with colorful icons
- Real-time timer during study sessions
- Study history and statistics
- Notes for each study session

## 📱 Mobile Friendly

The application is fully responsive and works great on:
- Tablets (perfect for kids)
- Smartphones
- Desktop computers

## 🔧 Technical Details

### Tech Stack
- **Backend**: Python Flask
- **Database**: MySQL with SQLAlchemy ORM
- **Frontend**: Bootstrap 5, HTML5, CSS3, JavaScript
- **Authentication**: Google OAuth 2.0
- **Icons**: Font Awesome
- **Styling**: Custom CSS with kid-friendly animations

### Database Schema
- **Users**: Google OAuth user information
- **Books**: Reading log with summaries
- **Study Sessions**: Time tracking with subjects and notes

### Security Features
- Google OAuth authentication
- CSRF protection
- SQL injection prevention via ORM
- Secure session management

## 🛠️ Development

### Project Structure
```
reading_tracker/
├── app.py                 # Main Flask application
├── config.py             # Configuration settings
├── requirements.txt      # Python dependencies
├── database.sql          # MySQL schema
├── static/
│   ├── css/
│   │   └── style.css    # Kid-friendly styles
│   └── js/
│       └── timer.js     # Timer functionality
└── templates/
    ├── base.html        # Base template
    ├── login.html       # Login page
    ├── dashboard.html   # Main dashboard
    ├── books.html       # Book management
    └── study_sessions.html # Study tracking
```

### Adding New Features

1. **New Subjects**: Update the `subject` enum in `database.sql` and add corresponding icons in templates
2. **Reading Goals**: Extend the Book model to include reading goals and progress tracking
3. **Parent Dashboard**: Create admin views for parents to monitor progress
4. **Rewards System**: Add achievements and badges for reading milestones

## 🎯 Usage Tips

### For Parents
- Help your child set up their account using your Gmail
- Review their reading summaries together
- Encourage consistent study time tracking
- Celebrate reading and study achievements

### For Kids
- Write fun summaries about books you read
- Use the timer to track homework and study time
- Try to study different subjects throughout the week
- Add notes about what you learned during study sessions

## 🐛 Troubleshooting

### Common Issues

1. **Database Connection Error**
   - Check MySQL is running
   - Verify database credentials in `.env`
   - Ensure database `reading_tracker` exists

2. **Google Login Not Working**
   - Verify `GOOGLE_CLIENT_ID` in `.env`
   - Check OAuth redirect URIs in Google Console
   - Ensure domain is authorized

3. **Timer Not Starting**
   - Check browser console for JavaScript errors
   - Ensure Flask routes are responding correctly
   - Verify database connection for study sessions

## 📈 Future Enhancements

- 📊 Advanced progress charts and analytics
- 🏆 Achievement badges and rewards system
- 📖 Book recommendations based on reading history
- 👨‍👩‍👧‍👦 Family accounts with multiple children
- 📱 Mobile app version
- 🔔 Study reminders and notifications
- 📚 Integration with library systems
- 🎮 Gamification elements

## 🤝 Contributing

Feel free to submit issues and enhancement requests! This project is designed to be educational and fun for children.

## 📄 License

This project is created for educational purposes. Feel free to use and modify for personal use.

---

Happy Reading and Learning! 📚✨🎉
