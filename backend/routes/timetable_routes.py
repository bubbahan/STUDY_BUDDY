from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import User, Subject, Timetable
from database import db
from datetime import date, timedelta

timetable_bp = Blueprint("timetable", __name__)


# =============================
# GENERATE TIMETABLE
# (frequency-weighted, exam-date-priority)
# =============================
@timetable_bp.route("/generate", methods=["POST"])
@jwt_required()
def generate_timetable():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)

    if not user:
        return jsonify({"message": "User not found"}), 404

    subjects = Subject.query.filter_by(user_id=user_id).all()

    if not subjects:
        return jsonify({"message": "No subjects found. Please add subjects first."}), 400

    today = date.today()

    # Determine reference exam date:
    # Use nearest subject exam_date, or user.exam_date, or 30 days
    subject_exam_dates = [s.exam_date for s in subjects if s.exam_date]
    if subject_exam_dates:
        nearest_exam = min(subject_exam_dates)
    elif user.exam_date:
        nearest_exam = user.exam_date
    else:
        nearest_exam = today + timedelta(days=30)

    days_remaining = (nearest_exam - today).days
    if days_remaining <= 0:
        days_remaining = 30  # Default fallback if exam already passed

    days_to_generate = min(days_remaining, 30)
    study_hours = user.study_hours_per_day or 4

    # Build weighted pool of subjects (repeated by frequency)
    total_weight = sum(s.frequency or 1 for s in subjects)

    # Sort by nearest exam date first (priority boost)
    def exam_priority(s):
        if s.exam_date:
            return (s.exam_date - today).days
        return 9999  # no exam date = lowest priority

    subjects_sorted = sorted(subjects, key=exam_priority)

    # Clear old timetable
    Timetable.query.filter_by(user_id=user_id).delete()

    for i in range(days_to_generate):
        current_date = today + timedelta(days=i)
        daily_hours_assigned = 0.0

        for s in subjects_sorted:
            freq = s.frequency or 1

            # Weight-based hours for this subject today
            weight_share = freq / total_weight
            subject_hours = round(study_hours * weight_share, 1)

            # Use per-subject study_goal if provided (parse numeric part)
            if s.study_goal:
                try:
                    parsed = float("".join(c for c in s.study_goal if c.isdigit() or c == "."))
                    if parsed > 0:
                        subject_hours = parsed
                except (ValueError, TypeError):
                    pass

            if subject_hours <= 0:
                subject_hours = 0.5

            # Exam-proximity boost: if exam within 7 days, add 20%
            if s.exam_date:
                days_to_exam = (s.exam_date - current_date).days
                if 0 <= days_to_exam <= 7:
                    subject_hours = round(subject_hours * 1.2, 1)

            # Only schedule subject on certain days based on frequency
            # frequency=1 → every day, frequency=2 → high priority (always include)
            # For frequency weighting: skip lower-frequency subjects on some days
            if freq < total_weight:
                # Skip subject on days where it doesn't fit the pattern
                # Use modulo: subject scheduled every (total_weight // freq) days
                interval = max(1, round(total_weight / freq))
                if (i % interval) != (s.id % interval):
                    continue

            schedule = Timetable(
                date=current_date,
                subject=s.name,
                planned_hours=subject_hours,
                user_id=user_id
            )
            db.session.add(schedule)
            daily_hours_assigned += subject_hours

    db.session.commit()

    return jsonify({
        "message": f"Timetable generated for {days_to_generate} days with frequency-based scheduling.",
        "days": days_to_generate,
        "subjects": len(subjects)
    })


# =============================
# GET TIMETABLE
# =============================
@timetable_bp.route("", methods=["GET"])
@jwt_required()
def get_timetable():
    user_id = int(get_jwt_identity())

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