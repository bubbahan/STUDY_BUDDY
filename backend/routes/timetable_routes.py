from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import User, Subject, Timetable
from database import db
from datetime import date, timedelta

timetable_bp = Blueprint("timetable", __name__)


# =============================
# GENERATE TIMETABLE
# =============================
@timetable_bp.route("/generate", methods=["POST"])
@jwt_required()
def generate_timetable():
    user_id = int(get_jwt_identity())   # FIXED: cast to int
    user = User.query.get(user_id)

    if not user:
        return jsonify({"message": "User not found"}), 404

    subjects = Subject.query.filter_by(user_id=user_id).all()

    if not subjects:
        return jsonify({"message": "No subjects found. Please add subjects during registration."}), 400

    if not user.exam_date:
        return jsonify({"message": "No exam date set. Please update your settings with an exam date."}), 400

    days_remaining = (user.exam_date - date.today()).days

    if days_remaining <= 0:
        return jsonify({"message": "Exam date has already passed. Please update your exam date in Settings."}), 400

    total_subjects = len(subjects)
    study_hours = user.study_hours_per_day or 4
    hours_per_subject = round(study_hours / total_subjects, 1)

    # Clear old timetable
    Timetable.query.filter_by(user_id=user_id).delete()

    days_to_generate = min(days_remaining, 30)  # Max 30 days
    for i in range(days_to_generate):
        for subject in subjects:
            schedule = Timetable(
                date=date.today() + timedelta(days=i),
                subject=subject.name,
                planned_hours=hours_per_subject,
                user_id=user_id
            )
            db.session.add(schedule)

    db.session.commit()

    return jsonify({
        "message": f"Timetable generated for {days_to_generate} days across {total_subjects} subjects.",
        "days": days_to_generate,
        "subjects": total_subjects
    })


# =============================
# GET TIMETABLE
# =============================
@timetable_bp.route("", methods=["GET"])
@jwt_required()
def get_timetable():
    user_id = int(get_jwt_identity())   # FIXED: cast to int

    entries = Timetable.query.filter_by(user_id=user_id).order_by(Timetable.date).all()

    result = []
    for entry in entries:
        result.append({
            "id": entry.id,
            "date": str(entry.date),
            "subject": entry.subject,
            "planned_hours": entry.planned_hours
        })

    return jsonify(result)