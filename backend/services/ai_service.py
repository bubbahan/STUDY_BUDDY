import requests
from flask import current_app


class AIService:
    """AI service using OpenRouter API (OpenAI-compatible endpoint)."""

    @staticmethod
    def _call(messages: list, temperature: float = 0.7, api_key_override: str = None) -> str:
        """
        Send a messages list to OpenRouter and return the reply text.
        api_key_override: if provided, uses the user-supplied key instead of server config.
        """
        api_key = api_key_override or current_app.config.get("OPENROUTER_API_KEY", "")
        if not api_key:
            raise RuntimeError(
                "No OpenRouter API key configured. "
                "Please enter your API key in the AI Assistant page."
            )

        model = current_app.config.get("OPENROUTER_MODEL", "openai/gpt-3.5-turbo")
        base_url = current_app.config.get(
            "OPENROUTER_BASE_URL",
            "https://openrouter.ai/api/v1/chat/completions"
        )

        response = requests.post(
            base_url,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "http://localhost:5000",
                "X-Title": "StudyBuddy"
            },
            json={
                "model": model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": 1200
            },
            timeout=30
        )

        if response.status_code != 200:
            raise RuntimeError(
                f"OpenRouter returned {response.status_code}. "
                f"Check your API key and try again."
            )

        data = response.json()
        return data["choices"][0]["message"]["content"].strip()

    # ------------------------------------------------------------------
    # AI TIMETABLE GENERATOR
    # ------------------------------------------------------------------
    @staticmethod
    def generate_timetable(
        subjects: list,
        study_hours_per_day: int,
        days_remaining: int,
        preference: str,
        exam_date: str,
        api_key_override: str = None
    ) -> str:
        subject_list = ", ".join(subjects) if subjects else "General Studies"
        prompt = f"""You are an expert academic planner and study coach.

A student needs a detailed study timetable with the following details:
- Subjects: {subject_list}
- Available study hours per day: {study_hours_per_day} hours
- Study preference: {preference} (morning or night)
- Days remaining until exam: {days_remaining} days
- Exam date: {exam_date}

Please generate:
1. A **weekly study schedule** (Mon-Sun) as a markdown table showing which subject to study each day and for how many hours.
2. **Priority ranking** of subjects from most to least important.
3. **3 specific actionable tips** for this student's timeline and preference.

Be concise, practical, and encouraging."""

        messages = [
            {"role": "system", "content": "You are a helpful academic planning assistant. Always format with markdown."},
            {"role": "user", "content": prompt}
        ]
        return AIService._call(messages, temperature=0.6, api_key_override=api_key_override)

    # ------------------------------------------------------------------
    # AI STUDY TIPS
    # ------------------------------------------------------------------
    @staticmethod
    def get_study_tips(
        name: str,
        subjects: list,
        preparation_percent: float,
        stress_level: str,
        streak: int,
        total_sessions: int,
        weak_areas: list,
        api_key_override: str = None
    ) -> str:
        subject_list = ", ".join(subjects) if subjects else "unknown subjects"
        weak_list = ", ".join(weak_areas) if weak_areas else "none detected"

        prompt = f"""You are a supportive and motivating academic coach for a student named {name}.

Their current stats:
- Subjects: {subject_list}
- Preparation: {preparation_percent}% complete
- Stress level: {stress_level}
- Current streak: {streak} days
- Sessions completed: {total_sessions}
- Weak areas: {weak_list}

Provide:
1. **Motivational message** (2 sentences) tailored to their stats.
2. **5 personalized study tips** targeting their weak areas and stress.
3. **One specific technique** (Pomodoro, spaced repetition, Feynman, etc.) to use right now.

Keep it friendly, specific, and under 300 words. Use markdown formatting."""

        messages = [
            {"role": "system", "content": "You are a motivating, friendly academic coach. Use markdown."},
            {"role": "user", "content": prompt}
        ]
        return AIService._call(messages, temperature=0.75, api_key_override=api_key_override)
