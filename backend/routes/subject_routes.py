from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import Subject, User
from database import db
from datetime import datetime

subject_bp = Blueprint("subjects", __name__)


# =============================
# GET ALL SUBJECTS
# =============================
@subject_bp.route("/", methods=["GET"])
@jwt_required()
def get_subjects():
    user_id = int(get_jwt_identity())
    subjects = Subject.query.filter_by(user_id=user_id).all()
    return jsonify([_serialize(s) for s in subjects])


# =============================
# GET SINGLE SUBJECT
# =============================
@subject_bp.route("/<int:subject_id>", methods=["GET"])
@jwt_required()
def get_subject(subject_id):
    user_id = int(get_jwt_identity())
    subject = Subject.query.filter_by(id=subject_id, user_id=user_id).first()
    if not subject:
        return jsonify({"message": "Subject not found"}), 404
    return jsonify(_serialize(subject))


# =============================
# ADD SUBJECT
# =============================
@subject_bp.route("/", methods=["POST"])
@jwt_required()
def add_subject():
    user_id = int(get_jwt_identity())
    data = request.get_json()
    name = (data.get("name") or "").strip()

    if not name:
        return jsonify({"message": "Subject name is required"}), 400

    existing = Subject.query.filter_by(user_id=user_id, name=name).first()
    if existing:
        return jsonify({"message": f"Subject '{name}' already exists"}), 400

    # Parse exam_date
    exam_date = None
    if data.get("exam_date"):
        try:
            exam_date = datetime.strptime(data["exam_date"], "%Y-%m-%d").date()
        except ValueError:
            return jsonify({"message": "Invalid exam_date format. Use YYYY-MM-DD"}), 400

    subject = Subject(
        name=name,
        units=data.get("units", 1),
        difficulty=data.get("difficulty", "Medium"),
        frequency=int(data.get("frequency", 1)),
        exam_date=exam_date,
        study_goal=(data.get("study_goal") or "").strip() or None,
        user_id=user_id
    )
    db.session.add(subject)
    db.session.commit()
    return jsonify({"message": "Subject added", **_serialize(subject)}), 201


# =============================
# UPDATE SUBJECT
# =============================
@subject_bp.route("/<int:subject_id>", methods=["PUT"])
@jwt_required()
def update_subject(subject_id):
    user_id = int(get_jwt_identity())
    subject = Subject.query.filter_by(id=subject_id, user_id=user_id).first()

    if not subject:
        return jsonify({"message": "Subject not found"}), 404

    data = request.get_json()

    if "name" in data and data["name"]:
        new_name = data["name"].strip()
        # Check uniqueness excluding self
        dup = Subject.query.filter_by(user_id=user_id, name=new_name).first()
        if dup and dup.id != subject_id:
            return jsonify({"message": f"Subject '{new_name}' already exists"}), 400
        subject.name = new_name

    if "difficulty" in data:
        subject.difficulty = data["difficulty"]
    if "frequency" in data:
        subject.frequency = int(data["frequency"])
    if "study_goal" in data:
        subject.study_goal = (data["study_goal"] or "").strip() or None
    if "exam_date" in data:
        if data["exam_date"]:
            try:
                subject.exam_date = datetime.strptime(data["exam_date"], "%Y-%m-%d").date()
            except ValueError:
                return jsonify({"message": "Invalid exam_date format. Use YYYY-MM-DD"}), 400
        else:
            subject.exam_date = None

    db.session.commit()
    return jsonify({"message": "Subject updated", **_serialize(subject)})


# =============================
# DELETE SUBJECT
# =============================
@subject_bp.route("/<int:subject_id>", methods=["DELETE"])
@jwt_required()
def delete_subject(subject_id):
    user_id = int(get_jwt_identity())
    subject = Subject.query.filter_by(id=subject_id, user_id=user_id).first()

    if not subject:
        return jsonify({"message": "Subject not found"}), 404

    db.session.delete(subject)
    db.session.commit()
    return jsonify({"message": "Subject removed"})


# =============================
# HELPER
# =============================
def _serialize(s):
    return {
        "id": s.id,
        "name": s.name,
        "units": s.units,
        "difficulty": s.difficulty or "Medium",
        "frequency": s.frequency or 1,
        "exam_date": str(s.exam_date) if s.exam_date else None,
        "study_goal": s.study_goal or ""
    }
