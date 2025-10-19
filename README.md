# 🚀 Kedar's Development Projects

This repository contains two main learning and development projects focused on practical applications and skill building.

---

## 📖 Section 1: Reading & Study Tracker

**🔗 [View Full Documentation](./reading_tracker/README.md)**

A kid-friendly web application designed to help children track their reading books and study time across different subjects. Perfect for parents who want to monitor and encourage their child's learning habits.

**✅ Status**: Fully functional with SQLite database and working Flask application!

### ✨ Features
- **📚 Book Tracking**: Log books with titles, authors, and personal summaries
- **⏰ Study Timer**: Real-time start/stop timer for study sessions
- **🎯 Subject Categories**: Maths, English, Science, Writing, Social Studies
- **🎨 Kid-Friendly Design**: Colorful, intuitive interface with emojis and animations
- **🔐 Google Authentication**: Secure login using Gmail accounts (with demo mode)
- **📊 Progress Tracking**: View study statistics and reading history
- **📱 Mobile Responsive**: Works great on tablets, phones, and desktop

### 🛠️ Tech Stack
- **Backend**: Python Flask, SQLAlchemy ORM
- **Database**: MySQL (with SQLite option for demo)
- **Frontend**: Bootstrap 5, HTML5, CSS3, JavaScript
- **Authentication**: Google OAuth 2.0
- **Styling**: Custom CSS with kid-friendly animations

### 🚀 Quick Start
```bash
cd reading_tracker
pip install -r requirements.txt
python init_db.py    # Initialize SQLite database
python app.py        # Start the application
```

Then visit `http://localhost:5000` in your browser to start tracking!

### 📁 Project Structure
```
reading_tracker/
├── app.py                  # Main Flask application
├── init_db.py             # Database initialization script
├── config.py              # Application configuration
├── database.sql           # MySQL schema (reference)
├── reading_tracker.db     # SQLite database (auto-created)
├── static/                # CSS styles and JavaScript
├── templates/             # HTML templates
└── README.md             # 📖 Full Documentation & Setup Guide
```

**🎯 [Get Started with Reading Tracker →](./reading_tracker/)**

---

## 🤖 Section 2: AI Learning & Development

**🔗 [View Full Documentation](./learn%20ai/README.md)**

A comprehensive learning journey into Agentic AI, featuring practical examples, foundational concepts, and hands-on projects to build real-world AI applications.

### 🎯 Learning Objectives
- **🧠 AI Foundations**: Core concepts of agentic AI systems
- **🛠️ Practical Examples**: Working code samples and implementations
- **🔧 Tool Integration**: Building AI agents with various tools and APIs
- **🚀 Project Development**: Real-world applications and use cases

### 📚 Learning Structure
- **Foundations**: Core AI concepts and theory
- **Examples**: Step-by-step code tutorials
- **Projects**: Practical applications to build
- **Resources**: Learning materials and references

### 🗂️ Project Organization
```
learn ai/
├── foundations/            # Core AI concepts and theory
│   └── agentic_ai_concepts.md
├── examples/              # Practical code examples
│   ├── 01_hello_agent.py
│   └── 02_agent_with_tools.py
├── projects/              # Project ideas and implementations
│   └── project_ideas.md
├── resources/             # Learning materials
│   └── learning_checklist.md
├── setup/                 # Environment setup guides
│   ├── install_guide.md
│   └── test_environment.py
└── requirements.txt       # Python dependencies
```

### 🚀 Getting Started
```bash
cd "learn ai"
pip install -r requirements.txt
python setup/test_environment.py  # Verify setup
python examples/01_hello_agent.py  # Run first example
```

**🤖 [Start Learning AI →](./learn%20ai/)**

---

## 🌟 Development Journey

This repository represents a learning journey that combines:
- **Family-focused Development**: Building tools that help with real-world needs (Reading Tracker)
- **Cutting-edge Technology**: Exploring AI and agent-based systems
- **Practical Application**: Learning by building actual working projects
- **Documentation**: Maintaining clear guides and examples for future reference

Both projects demonstrate different aspects of modern development:
- **Full-stack Web Development** (Reading Tracker)
- **AI/ML Integration** (Learn AI)
- **User Experience Design** (Kid-friendly interfaces)
- **Project Organization** (Clean, maintainable code structure)

---

## 🤝 Contributing & Learning

Feel free to explore, learn from, or contribute to these projects. They're designed to be educational and practical, perfect for:
- Parents looking for child-friendly tracking apps
- Developers learning Flask web development
- AI enthusiasts exploring agentic systems
- Anyone interested in well-documented, practical code examples

---

**Happy Coding & Learning!** 🎉👨‍💻📚🤖