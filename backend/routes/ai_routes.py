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
    """Generate an AI-powered personalized timetable.
    Accepts optional JSON body to override defaults with custom inputs.
    """
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404

    data = request.get_json(silent=True) or {}

    # --- Custom subjects from the frontend (with priorities) ---
    custom_subjects = data.get("subjects")   # list of {name, priority, notes}
    if custom_subjects:
        subject_details = custom_subjects
    else:
        db_subjects = Subject.query.filter_by(user_id=user_id).all()
        if not db_subjects:
            return jsonify({"message": "No subjects found. Add subjects first."}), 400
        subject_details = [{"name": s.name, "priority": "Medium", "notes": ""} for s in db_subjects]

    # --- Timeline ---
    custom_exam_date = data.get("exam_date")
    if custom_exam_date:
        try:
            from datetime import datetime
            exam_dt = datetime.strptime(custom_exam_date, "%Y-%m-%d").date()
            days_remaining = (exam_dt - date.today()).days
            exam_date_str = custom_exam_date
        except ValueError:
            return jsonify({"message": "Invalid exam date format (use YYYY-MM-DD)"}), 400
    elif user.exam_date:
        days_remaining = (user.exam_date - date.today()).days
        exam_date_str = str(user.exam_date)
    else:
        return jsonify({"message": "No exam date set. Update it in Settings or enter one above."}), 400

    if days_remaining <= 0:
        return jsonify({"message": "Exam date has already passed. Update it in Settings or enter a future date."}), 400

    # --- Other params ---
    study_hours = data.get("study_hours") or user.study_hours_per_day or 4
    preference = data.get("preference") or user.preference or "morning"
    extra_instructions = data.get("instructions", "")

    try:
        result = AIService.generate_timetable(
            subject_details=subject_details,
            study_hours_per_day=study_hours,
            days_remaining=days_remaining,
            preference=preference,
            exam_date=exam_date_str,
            extra_instructions=extra_instructions
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
    """Get personalized AI study tips."""
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

    weak_areas = []
    for s in sessions:
        if s.actual_time is not None and s.planned_time and s.planned_time > 0:
            if s.actual_time / s.planned_time < 0.7 and s.subject not in weak_areas:
                weak_areas.append(s.subject)
    for w in WeakArea.query.filter_by(user_id=user_id).all():
        if w.subject not in weak_areas:
            weak_areas.append(w.subject)

    try:
        result = AIService.get_study_tips(
            name=user.name or "Student",
            subjects=subject_names,
            preparation_percent=prep_pct,
            stress_level=stress,
            streak=user.streak or 0,
            total_sessions=len(sessions),
            weak_areas=weak_areas
        )
        return jsonify({"result": result})
    except RuntimeError as e:
        return jsonify({"message": str(e)}), 503
