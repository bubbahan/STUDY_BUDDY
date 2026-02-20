from models import StudySession, WeakArea
from database import db


class WeakAreaEngine:

    @staticmethod
    def detect_weak_areas(user_id):
        sessions = StudySession.query.filter_by(user_id=user_id).all()

        weak_count = 0

        for session in sessions:
            if session.actual_time < session.planned_time * 0.7:
                weak = WeakArea(
                    subject=session.subject,
                    issue_type="Low Study Time",
                    severity="High",
                    user_id=user_id
                )
                db.session.add(weak)
                weak_count += 1

        db.session.commit()

        return {
            "weak_sessions_detected": weak_count
        }