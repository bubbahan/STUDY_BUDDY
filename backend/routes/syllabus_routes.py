from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import Syllabus, Subject
from database import db

syllabus_bp = Blueprint("syllabus", __name__)


# =============================
# GET TOPICS FOR SUBJECT
# =============================
@syllabus_bp.route("/<int:subject_id>", methods=["GET"])
@jwt_required()
def get_topics(subject_id):
    user_id = int(get_jwt_identity())

    # Ensure subject belongs to user
    subject = Subject.query.filter_by(id=subject_id, user_id=user_id).first()
    if not subject:
        return jsonify({"message": "Subject not found"}), 404

    topics = Syllabus.query.filter_by(subject_id=subject_id).order_by(Syllabus.created_at).all()
    total = len(topics)
    done = sum(1 for t in topics if t.completed)

    return jsonify({
        "topics": [_serialize(t) for t in topics],
        "total": total,
        "completed": done,
        "percent": round((done / total) * 100) if total > 0 else 0
    })


# =============================
# ADD TOPIC
# =============================
@syllabus_bp.route("/<int:subject_id>", methods=["POST"])
@jwt_required()
def add_topic(subject_id):
    user_id = int(get_jwt_identity())

    subject = Subject.query.filter_by(id=subject_id, user_id=user_id).first()
    if not subject:
        return jsonify({"message": "Subject not found"}), 404

    data = request.get_json()
    topic_name = (data.get("topic_name") or "").strip()

    if not topic_name:
        return jsonify({"message": "topic_name is required"}), 400

    topic = Syllabus(topic_name=topic_name, subject_id=subject_id)
    db.session.add(topic)
    db.session.commit()
    return jsonify({"message": "Topic added", **_serialize(topic)}), 201


# =============================
# TOGGLE COMPLETION
# =============================
@syllabus_bp.route("/<int:topic_id>/toggle", methods=["PUT"])
@jwt_required()
def toggle_topic(topic_id):
    user_id = int(get_jwt_identity())

    topic = Syllabus.query.get(topic_id)
    if not topic:
        return jsonify({"message": "Topic not found"}), 404

    # Verify ownership via subject
    subject = Subject.query.filter_by(id=topic.subject_id, user_id=user_id).first()
    if not subject:
        return jsonify({"message": "Unauthorized"}), 403

    topic.completed = not topic.completed
    db.session.commit()
    return jsonify({"message": "Updated", **_serialize(topic)})


# =============================
# DELETE TOPIC
# =============================
@syllabus_bp.route("/<int:topic_id>", methods=["DELETE"])
@jwt_required()
def delete_topic(topic_id):
    user_id = int(get_jwt_identity())

    topic = Syllabus.query.get(topic_id)
    if not topic:
        return jsonify({"message": "Topic not found"}), 404

    subject = Subject.query.filter_by(id=topic.subject_id, user_id=user_id).first()
    if not subject:
        return jsonify({"message": "Unauthorized"}), 403

    db.session.delete(topic)
    db.session.commit()
    return jsonify({"message": "Topic deleted"})


# =============================
# HELPER
# =============================
def _serialize(t):
    return {
        "id": t.id,
        "topic_name": t.topic_name,
        "completed": t.completed,
        "subject_id": t.subject_id
    }
