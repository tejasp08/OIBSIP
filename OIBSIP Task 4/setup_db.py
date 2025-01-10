from app import app, db

# Use the application context to bind the app
with app.app_context():
    db.create_all()
    print("Database and tables created successfully.")

