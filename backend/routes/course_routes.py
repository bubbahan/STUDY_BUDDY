from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import Course, Enrollment
from database import db

course_bp = Blueprint("course", __name__)


# =============================
# LIST ALL COURSES
# =============================
@course_bp.route("", methods=["GET"])
@jwt_required()
def list_courses():
    user_id = int(get_jwt_identity())   # FIXED: cast to int

    courses = Course.query.all()
    enrollments = Enrollment.query.filter_by(user_id=user_id).all()
    enrolled_ids = {e.course_id: e for e in enrollments}

    result = []
    for c in courses:
        enrollment = enrolled_ids.get(c.id)
        result.append({
            "id": c.id,
            "title": c.title,
            "level": c.level,
            "total_units": c.total_units,
            "required_hours": c.required_hours,
            "enrolled": c.id in enrolled_ids,
            "progress_units": enrollment.progress_units if enrollment else 0,
            "completed": enrollment.completed if enrollment else False
        })

    return jsonify(result)


# =============================
# ENROLL COURSE
# =============================
@course_bp.route("/enroll/<int:course_id>", methods=["POST"])
@jwt_required()
def enroll(course_id):
    user_id = int(get_jwt_identity())   # FIXED: cast to int

    course = Course.query.get(course_id)
    if not course:
        return jsonify({"message": "Course not found"}), 404

    existing = Enrollment.query.filter_by(user_id=user_id, course_id=course_id).first()
    if existing:
        return jsonify({"message": "Already enrolled"}), 400

    enrollment = Enrollment(
        user_id=user_id,
        course_id=course_id
    )

    db.session.add(enrollment)
    db.session.commit()

    return jsonify({"message": "Enrolled successfully"})


# =============================
# UPDATE PROGRESS
# =============================
@course_bp.route("/progress/<int:course_id>", methods=["POST"])
@jwt_required()
def update_progress(course_id):
    user_id = int(get_jwt_identity())   # FIXED: cast to int
    data = request.get_json()

    enrollment = Enrollment.query.filter_by(
        user_id=user_id,
        course_id=course_id
    ).first()

    if not enrollment:
        return jsonify({"message": "Not enrolled in this course"}), 400

    units_to_add = int(data.get("units_completed", 1))
    enrollment.progress_units = min(
        enrollment.progress_units + units_to_add,
        enrollment.course.total_units
    )

    # Completion logic
    if enrollment.progress_units >= enrollment.course.total_units:
        enrollment.completed = True

        # Unlock next course
        if enrollment.course.next_course_id:
            existing_next = Enrollment.query.filter_by(
                user_id=user_id, course_id=enrollment.course.next_course_id
            ).first()
            if not existing_next:
                next_enrollment = Enrollment(
                    user_id=user_id,
                    course_id=enrollment.course.next_course_id
                )
                db.session.add(next_enrollment)

    db.session.commit()

    return jsonify({
        "message": "Progress updated",
        "progress_units": enrollment.progress_units,
        "completed": enrollment.completed
    })