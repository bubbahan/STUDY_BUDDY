from datetime import date, timedelta
from models import User, Subject, Timetable
from database import db


class PlanningEngine:

    @staticmethod
    def generate_plan(user_id):
        user = User.query.get(user_id)
        subjects = Subject.query.filter_by(user_id=user_id).all()

        days_remaining = (user.exam_date - date.today()).days

        if days_remaining <= 0:
            return {"error": "Invalid exam date"}

        total_subjects = len(subjects)
        hours_per_subject = user.study_hours_per_day / total_subjects

        # Productivity Window Logic
        if user.preference == "morning":
            session_type = "Deep Focus"
        else:
            session_type = "Night Focus"

        # Clear old timetable
        Timetable.query.filter_by(user_id=user_id).delete()

        for i in range(days_remaining):
            for subject in subjects:
                schedule = Timetable(
                    date=date.today() + timedelta(days=i),
                    subject=f"{subject.name} ({session_type})",
                    planned_hours=hours_per_subject,
                    user_id=user_id
                )
                db.session.add(schedule)

        db.session.commit()

        return {"message": "Adaptive timetable generated successfully"}