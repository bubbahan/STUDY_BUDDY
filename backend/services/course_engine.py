from models import Enrollment, Course
from database import db


class CourseEngine:

    @staticmethod
    def check_completion(user_id, course_id):
        enrollment = Enrollment.query.filter_by(
            user_id=user_id,
            course_id=course_id
        ).first()

        course = Course.query.get(course_id)

        if enrollment.progress_units >= course.total_units:
            enrollment.completed = True

            next_course = None

            if course.next_course_id:
                next_course = Enrollment(
                    user_id=user_id,
                    course_id=course.next_course_id
                )
                db.session.add(next_course)

            db.session.commit()

            return {
                "completed": True,
                "next_course_unlocked": bool(course.next_course_id)
            }

        return {
            "completed": False
        }