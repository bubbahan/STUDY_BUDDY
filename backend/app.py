import os
from flask import Flask, send_from_directory
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from config import Config
from database import db

# Import models so tables register
import models


def seed_courses(app):
    """Seed initial course data if none exists."""
    with app.app_context():
        from models import Course
        if Course.query.count() == 0:
            courses = [
                Course(title="Python Basics", level=1, total_units=10, required_hours=5),
                Course(title="Data Structures", level=2, total_units=12, required_hours=8),
                Course(title="Algorithms", level=2, total_units=15, required_hours=10),
                Course(title="Web Development", level=1, total_units=8, required_hours=6),
                Course(title="Machine Learning Intro", level=3, total_units=20, required_hours=15),
                Course(title="Database Design", level=2, total_units=10, required_hours=7),
            ]
            for course in courses:
                db.session.add(course)
            db.session.commit()
            print("[StudyBuddy] Seeded 6 courses into the database.")


def create_app():
    app = Flask(__name__, static_folder=None)
    app.config.from_object(Config)

    # Use dedicated JWT secret key (avoids the HMAC short-key warning)
    app.config["JWT_SECRET_KEY"] = Config.JWT_SECRET_KEY
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = Config.JWT_ACCESS_TOKEN_EXPIRES

    # Extensions
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    JWTManager(app)
    db.init_app(app)

    # ------ Register Blueprints ------
    from routes.auth_routes import auth_bp
    from routes.user_routes import user_bp
    from routes.timetable_routes import timetable_bp
    from routes.analytics_routes import analytics_bp
    from routes.course_routes import course_bp
    from routes.session_routes import session_bp
    from routes.ai_routes import ai_bp

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(user_bp, url_prefix="/api/user")
    app.register_blueprint(timetable_bp, url_prefix="/api/timetable")
    app.register_blueprint(analytics_bp, url_prefix="/api/analytics")
    app.register_blueprint(course_bp, url_prefix="/api/courses")
    app.register_blueprint(session_bp, url_prefix="/api/session")
    app.register_blueprint(ai_bp, url_prefix="/api/ai")

    # ------ Serve Frontend Static Files ------
    frontend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend"))

    @app.route("/")
    def serve_index():
        return send_from_directory(frontend_dir, "index.html")

    @app.route("/<path:path>")
    def serve_frontend(path):
        return send_from_directory(frontend_dir, path)

    with app.app_context():
        db.create_all()

    seed_courses(app)

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)