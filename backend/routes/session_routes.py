from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import StudySession
from database import db
from services.gamification_engine import GamificationEngine

session_bp = Blueprint("session", __name__)


# =============================
# SAVE STUDY SESSION
# =============================
@session_bp.route("", methods=["POST"])
@jwt_required()
def save_session():
    user_id = int(get_jwt_identity())   # FIXED: cast to int
    data = request.get_json()

    subject = data.get("subject", "").strip()
    if not subject:
        return jsonify({"message": "Subject is required"}), 400

    actual_hours = float(data.get("actual_time", 0) or 0)
    planned_hours = float(data.get("planned_time", actual_hours) or actual_hours)
    unit_completed = int(data.get("unit_completed", 0) or 0)

    session = StudySession(
        subject=subject,
        unit_completed=unit_completed,
        planned_time=planned_hours,
        actual_time=actual_hours,
        user_id=user_id
    )

    db.session.add(session)
    db.session.commit()

    # Award XP for study time
    if actual_hours > 0:
        result = GamificationEngine.add_xp(user_id, actual_hours)
        GamificationEngine.update_streak(user_id)
        return jsonify({
            "message": "Session saved successfully",
            "xp_earned": result.get("xp_earned", 0),
            "level": result.get("current_level", 1),
            "xp": result.get("current_xp", 0)
        }), 201

    return jsonify({"message": "Session saved successfully"}), 201


# =============================
# GET ALL SESSIONS
# =============================
@session_bp.route("", methods=["GET"])
@session_bp.route("/all", methods=["GET"])
@jwt_required()
def get_sessions():
    user_id = int(get_jwt_identity())   # FIXED: cast to int
    sessions = StudySession.query.filter_by(user_id=user_id).order_by(StudySession.session_date.desc()).all()

    result = []
    for s in sessions:
        result.append({
            "id": s.id,
            "subject": s.subject,
            "planned_time": s.planned_time,
            "actual_time": s.actual_time,
            "unit_completed": s.unit_completed,
            "date": str(s.session_date) if s.session_date else None
        })

    return jsonify(result)
