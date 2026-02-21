from datetime import datetime
from database import db


# =========================
# USER MODEL
# =========================
class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

    study_hours_per_day = db.Column(db.Integer)
    sleep_time = db.Column(db.String(20))
    wake_time = db.Column(db.String(20))
    preference = db.Column(db.String(20))  # morning/night

    exam_date = db.Column(db.Date)

    # New fields
    profile_photo = db.Column(db.String(300))   # path to uploaded photo
    alarm_sound = db.Column(db.String(100), default="default")  # selected alarm sound

    level = db.Column(db.Integer, default=1)
    xp = db.Column(db.Integer, default=0)
    streak = db.Column(db.Integer, default=0)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    subjects = db.relationship("Subject", backref="user", lazy=True, cascade="all, delete-orphan")
    sessions = db.relationship("StudySession", backref="user", lazy=True)
    enrollments = db.relationship("Enrollment", backref="user", lazy=True)


# =========================
# SUBJECT MODEL (enhanced)
# =========================
class Subject(db.Model):
    __tablename__ = "subjects"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    units = db.Column(db.Integer, default=1)

    # New fields
    difficulty = db.Column(db.String(20), default="Medium")   # High / Medium / Low
    frequency = db.Column(db.Integer, default=1)               # how often to study (weight)
    exam_date = db.Column(db.Date)                             # per-subject exam date
    study_goal = db.Column(db.String(200))                     # optional goal text

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    # Cascade delete syllabus topics when subject is deleted
    topics = db.relationship("Syllabus", backref="subject", lazy=True, cascade="all, delete-orphan")


# =========================
# SYLLABUS MODEL (new)
# =========================
class Syllabus(db.Model):
    __tablename__ = "syllabus"

    id = db.Column(db.Integer, primary_key=True)
    topic_name = db.Column(db.String(200), nullable=False)
    completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    subject_id = db.Column(db.Integer, db.ForeignKey("subjects.id"), nullable=False)


# =========================
# TIMETABLE MODEL
# =========================
class Timetable(db.Model):
    __tablename__ = "timetable"

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date)
    subject = db.Column(db.String(100))
    planned_hours = db.Column(db.Float)
    completed = db.Column(db.Boolean, default=False)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)


# =========================
# STUDY SESSION MODEL
# =========================
class StudySession(db.Model):
    __tablename__ = "study_sessions"

    id = db.Column(db.Integer, primary_key=True)
    subject = db.Column(db.String(100))
    unit_completed = db.Column(db.Integer)
    planned_time = db.Column(db.Float)
    actual_time = db.Column(db.Float)

    session_date = db.Column(db.Date, default=datetime.utcnow)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)


# =========================
# WEAK AREA MODEL
# =========================
class WeakArea(db.Model):
    __tablename__ = "weak_areas"

    id = db.Column(db.Integer, primary_key=True)
    subject = db.Column(db.String(100))
    issue_type = db.Column(db.String(100))  # low_time, missed_target, etc.
    severity = db.Column(db.String(50))  # low/medium/high

    detected_on = db.Column(db.DateTime, default=datetime.utcnow)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)


# =========================
# COURSE MODEL (legacy)
# =========================
class Course(db.Model):
    __tablename__ = "courses"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150))
    level = db.Column(db.Integer)
    total_units = db.Column(db.Integer)
    required_hours = db.Column(db.Integer)

    next_course_id = db.Column(db.Integer, db.ForeignKey("courses.id"))


# =========================
# ENROLLMENT MODEL (legacy)
# =========================
class Enrollment(db.Model):
    __tablename__ = "enrollments"

    id = db.Column(db.Integer, primary_key=True)
    progress_units = db.Column(db.Integer, default=0)
    completed = db.Column(db.Boolean, default=False)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey("courses.id"), nullable=False)

    course = db.relationship("Course")