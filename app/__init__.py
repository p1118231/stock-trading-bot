from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from apscheduler.schedulers.background import BackgroundScheduler

db = SQLAlchemy()
scheduler = BackgroundScheduler()

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///trades.db'  # SQLite for simplicity
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    scheduler.start()

    with app.app_context():
        from .main import main  # Import blueprint
        app.register_blueprint(main)
        db.create_all()  # Create database tables

    return app
