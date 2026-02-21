import os
from flask import Flask, send_from_directory
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from config import Config
from database import db

# Import models so tables register
import models


def create_app():
    app = Flask(__name__, static_folder=None)
    app.config.from_object(Config)

    # Use dedicated JWT secret key
    app.config["JWT_SECRET_KEY"] = Config.JWT_SECRET_KEY
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = Config.JWT_ACCESS_TOKEN_EXPIRES

    # Upload folder for profile photos
    upload_folder = os.path.join(os.path.dirname(__file__), "uploads")
    app.config["UPLOAD_FOLDER"] = upload_folder
    os.makedirs(upload_folder, exist_ok=True)

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
    from routes.subject_routes import subject_bp
    from routes.syllabus_routes import syllabus_bp

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(user_bp, url_prefix="/api/user")
    app.register_blueprint(timetable_bp, url_prefix="/api/timetable")
    app.register_blueprint(analytics_bp, url_prefix="/api/analytics")
    app.register_blueprint(course_bp, url_prefix="/api/courses")
    app.register_blueprint(session_bp, url_prefix="/api/session")
    app.register_blueprint(ai_bp, url_prefix="/api/ai")
    app.register_blueprint(subject_bp, url_prefix="/api/subjects")
    app.register_blueprint(syllabus_bp, url_prefix="/api/syllabus")

    # ------ Serve Uploaded Files ------
    @app.route("/uploads/<path:filename>")
    def serve_uploads(filename):
        return send_from_directory(upload_folder, filename)

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

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)