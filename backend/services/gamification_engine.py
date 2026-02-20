from models import User
from database import db
from datetime import date


class GamificationEngine:

    XP_PER_HOUR = 10
    LEVEL_UP_XP = 100

    @staticmethod
    def add_xp(user_id, hours_studied):
        user = User.query.get(int(user_id))   # FIXED: cast to int
        if not user:
            return {"xp_earned": 0, "current_level": 1, "current_xp": 0}

        earned_xp = float(hours_studied) * GamificationEngine.XP_PER_HOUR
        user.xp = (user.xp or 0) + earned_xp

        # Level up logic — handle multiple level-ups in one session
        while user.xp >= GamificationEngine.LEVEL_UP_XP:
            user.level = (user.level or 1) + 1
            user.xp -= GamificationEngine.LEVEL_UP_XP

        db.session.commit()

        return {
            "xp_earned": earned_xp,
            "current_level": user.level,
            "current_xp": user.xp
        }

    @staticmethod
    def update_streak(user_id):
        user = User.query.get(int(user_id))   # FIXED: cast to int
        if not user:
            return {"current_streak": 0}

        user.streak = (user.streak or 0) + 1
        db.session.commit()

        return {
            "current_streak": user.streak
        }