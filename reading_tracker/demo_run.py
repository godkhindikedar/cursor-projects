#!/usr/bin/env python3
"""
Demo run script for the Reading & Study Tracker application
This sets up temporary environment variables for testing and enables demo mode
"""

import os
import sys

# Set temporary environment variables for demo
os.environ['SECRET_KEY'] = 'demo-secret-key-for-testing-change-me-in-production'
os.environ['DATABASE_URL'] = 'sqlite:///reading_tracker_demo.db'  # Use SQLite for demo
os.environ['GOOGLE_CLIENT_ID'] = 'demo-client-id.apps.googleusercontent.com'
os.environ['DEMO_MODE'] = 'true'  # Enable demo mode

def main():
    """Main function to start the demo application"""
    print("🚀 Starting Reading & Study Tracker Demo...")
    print("=" * 50)
    print("⚠️  This is a DEMO mode with temporary settings")
    print("   - Using SQLite database (no MySQL needed)")
    print("   - Demo login available (no Google setup needed)")
    print("   - Perfect for seeing the UI and functionality!")
    print("=" * 50)
    
    try:
        # Import the demo app
        from app_demo import app, db
        
        # Create all database tables
        with app.app_context():
            db.create_all()
            print("✅ Demo database created successfully!")
            
            # Create a demo user if it doesn't exist
            from app_demo import User, Book, StudySession
            demo_user = User.query.filter_by(email='demo@example.com').first()
            if not demo_user:
                demo_user = User(
                    email='demo@example.com',
                    name='Alex',
                    google_id='demo_user_123'
                )
                db.session.add(demo_user)
                db.session.commit()
                print("✅ Demo user created!")
                
                # Add some sample books
                sample_books = [
                    Book(title="The Cat in the Hat", author="Dr. Seuss", 
                         summary="A super fun story about a cat who visits on a rainy day! The cat made everything messy but then cleaned it all up. I loved the Thing One and Thing Two characters!", 
                         user_id=demo_user.id),
                    Book(title="Charlotte's Web", author="E.B. White", 
                         summary="This book made me cry happy tears! Charlotte the spider was so kind to Wilbur the pig. It taught me about friendship and being brave. Charlotte was a hero!", 
                         user_id=demo_user.id),
                    Book(title="Where the Wild Things Are", author="Maurice Sendak", 
                         summary="Max went on the coolest adventure ever! The wild things looked scary but they were actually friendly. I wish I could sail to their island too!", 
                         user_id=demo_user.id)
                ]
                
                for book in sample_books:
                    db.session.add(book)
                
                # Add some sample study sessions
                from datetime import datetime, timedelta
                import random
                
                subjects = ['maths', 'english', 'science', 'writing', 'social_studies']
                session_notes = {
                    'maths': "Practiced multiplication tables and did some word problems. Getting faster!",
                    'english': "Read a chapter and answered comprehension questions. Love this book!",
                    'science': "Learned about the solar system. Jupiter is HUGE! 🪐",
                    'writing': "Wrote a story about my pet hamster's adventures.",
                    'social_studies': "Studied different countries and their flags. So many colors!"
                }
                
                # Create study sessions from the past few days
                for i in range(8):
                    days_ago = random.randint(0, 7)
                    start_time = datetime.utcnow() - timedelta(days=days_ago, hours=random.randint(9, 16), minutes=random.randint(0, 59))
                    duration = random.randint(15, 45)
                    subject = random.choice(subjects)
                    
                    session = StudySession(
                        subject=subject,
                        start_time=start_time,
                        end_time=start_time + timedelta(minutes=duration),
                        duration_minutes=duration,
                        notes=session_notes.get(subject, "Had a great study session!"),
                        user_id=demo_user.id
                    )
                    db.session.add(session)
                
                db.session.commit()
                print("✅ Demo data added!")
        
        print("🌟 Starting the demo application...")
        print("📱 Open your browser and go to: http://localhost:5000")
        print("🎉 Use the 'Demo Login' button to explore the app!")
        print("🛑 Press Ctrl+C to stop the server")
        print("=" * 50)
        
        app.run(debug=True, host='0.0.0.0', port=5000)
        
    except KeyboardInterrupt:
        print("\n👋 Demo application stopped by user")
    except Exception as e:
        print(f"❌ Error starting demo application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
