from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import StudySession, User, WeakArea
from database import db

analytics_bp = Blueprint("analytics", __name__)


# =============================
# DASHBOARD ANALYTICS
# =============================
@analytics_bp.route("/dashboard", methods=["GET"])
@jwt_required()
def dashboard_analytics():
    user_id = int(get_jwt_identity())   # FIXED: cast to int
    user = User.query.get(user_id)

    if not user:
        return jsonify({"message": "User not found"}), 404

    sessions = StudySession.query.filter_by(user_id=user_id).all()

    total_planned = sum(s.planned_time or 0 for s in sessions)
    total_actual = sum(s.actual_time or 0 for s in sessions)

    preparation_percent = 0
    if total_planned > 0:
        preparation_percent = min((total_actual / total_planned) * 100, 100)

    # Stress prediction
    if preparation_percent < 40:
        stress = "High"
    elif preparation_percent < 70:
        stress = "Medium"
    else:
        stress = "Low"

    return jsonify({
        "name": user.name,
        "preparation_percent": round(preparation_percent, 2),
        "stress_level": stress,
        "streak": user.streak or 0,
        "level": user.level or 1,
        "xp": user.xp or 0,
        "total_study_hours": round(total_actual, 1),
        "total_sessions": len(sessions)
    })


# =============================
# WEAK AREAS
# =============================
@analytics_bp.route("/weak-areas", methods=["GET"])
@jwt_required()
def get_weak_areas():
    user_id = int(get_jwt_identity())   # FIXED: cast to int

    # Detect weak areas from sessions (actual < 70% of planned)
    sessions = StudySession.query.filter_by(user_id=user_id).all()
    weak_map = {}

    for s in sessions:
        if s.actual_time is not None and s.planned_time and s.planned_time > 0:
            ratio = s.actual_time / s.planned_time
            if ratio < 0.7:
                subject = s.subject
                if subject not in weak_map:
                    severity = "High" if ratio < 0.4 else "Medium"
                    weak_map[subject] = {"subject": subject, "issue_type": "Low Study Time", "severity": severity}

    # Also include previously saved weak areas
    saved_weak = WeakArea.query.filter_by(user_id=user_id).all()
    for w in saved_weak:
        if w.subject not in weak_map:
            weak_map[w.subject] = {
                "subject": w.subject,
                "issue_type": w.issue_type or "Low Study Time",
                "severity": w.severity or "Medium"
            }

    return jsonify(list(weak_map.values()))