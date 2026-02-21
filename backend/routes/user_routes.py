from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash
from models import User
from database import db

user_bp = Blueprint("user", __name__)

# =============================
# GET PROFILE
# =============================
@user_bp.route("/profile", methods=["GET"])
@jwt_required()
def get_profile():
    user_id = int(get_jwt_identity())   # FIXED: cast to int
    user = User.query.get(user_id)

    if not user:
        return jsonify({"message": "User not found"}), 404

    return jsonify({
        "name": user.name,
        "email": user.email,
        "level": user.level or 1,
        "xp": user.xp or 0,
        "streak": user.streak or 0,
        "exam_date": str(user.exam_date) if user.exam_date else None,
        "study_hours_per_day": user.study_hours_per_day or 4,
        "preference": user.preference or "morning",
        "sleep_time": user.sleep_time or "23:00",
        "wake_time": user.wake_time or "07:00"
    })


# =============================
# UPDATE PROFILE
# =============================
@user_bp.route("/update", methods=["PUT"])
@jwt_required()
def update_profile():
    user_id = int(get_jwt_identity())   # FIXED: cast to int
    user = User.query.get(user_id)

    if not user:
        return jsonify({"message": "User not found"}), 404

    data = request.get_json()

    if "name" in data and data["name"]:
        user.name = data["name"].strip()
    if "study_hours_per_day" in data:
        hours = data["study_hours_per_day"]
        if hours and 1 <= int(hours) <= 16:
            user.study_hours_per_day = int(hours)
    if "preference" in data:
        user.preference = data["preference"]
    if "sleep_time" in data:
        user.sleep_time = data["sleep_time"]
    if "wake_time" in data:
        user.wake_time = data["wake_time"]
    if "exam_date" in data:
        from datetime import datetime
        if data["exam_date"]:
            try:
                user.exam_date = datetime.strptime(data["exam_date"], "%Y-%m-%d").date()
            except ValueError:
                return jsonify({"message": "Invalid date format. Use YYYY-MM-DD"}), 400
        else:
            user.exam_date = None

    db.session.commit()
    return jsonify({"message": "Profile updated successfully"})


# =============================
# CHANGE PASSWORD
# =============================
@user_bp.route("/change-password", methods=["POST"])
@jwt_required()
def change_password():
    user_id = int(get_jwt_identity())   # FIXED: cast to int
    user = User.query.get(user_id)

    if not user:
        return jsonify({"message": "User not found"}), 404

    data = request.get_json()
    new_password = data.get("password", "")

    if not new_password or len(new_password) < 6:
        return jsonify({"message": "Password must be at least 6 characters"}), 400

    user.password = generate_password_hash(new_password)
    db.session.commit()
    return jsonify({"message": "Password changed successfully"})