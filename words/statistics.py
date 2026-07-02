from datetime import timedelta
from django.utils import timezone
from .models import StudySession


def get_current_streak(user):
    today = timezone.localdate()
    sessions = StudySession.objects.filter(user=user)

    study_days = {session.created_at.date() for session in sessions}

    current_day = today
    if current_day not in study_days:
        current_day -= timedelta(days=1)

    current_streak = 0

    while current_day in study_days:
        current_streak += 1
        current_day -= timedelta(days=1)

    return current_streak


def get_completed_sessions(user):
    return StudySession.objects.filter(user=user).count()





