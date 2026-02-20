from flask import Blueprint, request, jsonify
from models import User, Subject
from database import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token
from datetime import datetime

auth_bp = Blueprint("auth", __name__)

# =============================
# REGISTER
# =============================
@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()

    if User.query.filter_by(email=data["email"]).first():
        return jsonify({"message": "User already exists"}), 400

    hashed_password = generate_password_hash(data["password"])

    # Parse exam_date string to date object
    exam_date = None
    if data.get("exam_date"):
        try:
            exam_date = datetime.strptime(data["exam_date"], "%Y-%m-%d").date()
        except ValueError:
            return jsonify({"message": "Invalid exam date format"}), 400

    user = User(
        name=data["name"],
        email=data["email"],
        password=hashed_password,
        study_hours_per_day=data.get("study_hours_per_day", 4),
        sleep_time=data.get("sleep_time", "23:00"),
        wake_time=data.get("wake_time", "07:00"),
        preference=data.get("preference", "morning"),
        exam_date=exam_date
    )

    db.session.add(user)
    db.session.flush()  # Get user.id before commit

    # Create subjects if provided
    subjects_list = data.get("subjects", [])
    for subj_name in subjects_list:
        subj_name = subj_name.strip()
        if subj_name:
            subject = Subject(name=subj_name, units=1, user_id=user.id)
            db.session.add(subject)

    db.session.commit()

    return jsonify({"message": "User registered successfully"}), 201


# =============================
# LOGIN
# =============================
@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()

    user = User.query.filter_by(email=data["email"]).first()

    if not user or not check_password_hash(user.password, data["password"]):
        return jsonify({"message": "Invalid credentials"}), 401

    access_token = create_access_token(identity=str(user.id))

    return jsonify({
        "token": access_token,
        "name": user.name,
        "level": user.level,
        "xp": user.xp
    })