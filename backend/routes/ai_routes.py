from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import User, Subject, StudySession, WeakArea
from database import db
from services.ai_service import AIService
from datetime import date

ai_bp = Blueprint("ai", __name__)


# =============================
# AI TIMETABLE GENERATION
# =============================
@ai_bp.route("/timetable", methods=["POST"])
@jwt_required()
def ai_timetable():
    """Generate an AI-powered personalized timetable."""
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)

    if not user:
        return jsonify({"message": "User not found"}), 404

    subjects = Subject.query.filter_by(user_id=user_id).all()
    subject_names = [s.name for s in subjects]

    if not subject_names:
        return jsonify({"message": "No subjects found. Add subjects during registration."}), 400

    if not user.exam_date:
        return jsonify({"message": "No exam date set. Update it in Settings first."}), 400

    days_remaining = (user.exam_date - date.today()).days
    if days_remaining <= 0:
        return jsonify({"message": "Exam date has already passed. Update it in Settings."}), 400

    # Get user's API key from header (browser stores it locally, sends per-request)
    user_api_key = request.headers.get("X-OpenRouter-Key", "").strip()

    try:
        result = AIService.generate_timetable(
            subjects=subject_names,
            study_hours_per_day=user.study_hours_per_day or 4,
            days_remaining=days_remaining,
            preference=user.preference or "morning",
            exam_date=str(user.exam_date),
            api_key_override=user_api_key or None
        )
        return jsonify({"result": result})
    except RuntimeError as e:
        return jsonify({"message": str(e)}), 503


# =============================
# AI STUDY TIPS
# =============================
@ai_bp.route("/tips", methods=["POST"])
@jwt_required()
def ai_tips():
    """Get personalized AI study tips based on user stats."""
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)

    if not user:
        return jsonify({"message": "User not found"}), 404

    subjects = Subject.query.filter_by(user_id=user_id).all()
    subject_names = [s.name for s in subjects]

    sessions = StudySession.query.filter_by(user_id=user_id).all()
    total_planned = sum(s.planned_time or 0 for s in sessions)
    total_actual = sum(s.actual_time or 0 for s in sessions)
    prep_pct = round((total_actual / total_planned * 100), 1) if total_planned > 0 else 0
    prep_pct = min(prep_pct, 100)

    stress = "High" if prep_pct < 40 else ("Medium" if prep_pct < 70 else "Low")

    # Collect weak areas
    weak_areas = []
    for s in sessions:
        if s.actual_time is not None and s.planned_time and s.planned_time > 0:
            if s.actual_time / s.planned_time < 0.7 and s.subject not in weak_areas:
                weak_areas.append(s.subject)

    saved_weak = WeakArea.query.filter_by(user_id=user_id).all()
    for w in saved_weak:
        if w.subject not in weak_areas:
            weak_areas.append(w.subject)

    # Get user's API key from header
    user_api_key = request.headers.get("X-OpenRouter-Key", "").strip()

    try:
        result = AIService.get_study_tips(
            name=user.name or "Student",
            subjects=subject_names,
            preparation_percent=prep_pct,
            stress_level=stress,
            streak=user.streak or 0,
            total_sessions=len(sessions),
            weak_areas=weak_areas,
            api_key_override=user_api_key or None
        )
        return jsonify({"result": result})
    except RuntimeError as e:
        return jsonify({"message": str(e)}), 503
