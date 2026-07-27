import pytest

from datetime import timedelta
from words.models import WordSet, StudySession
from words.statistics import get_completed_sessions, get_current_streak
from django.utils import timezone

@pytest.mark.django_db
def test_get_completed_sessions_returns_only_current_users_sessions(django_user_model):
    user_1 = django_user_model.objects.create_user(username="jan", password="haslo")
    user_2 = django_user_model.objects.create_user(username="adam", password="haslo")
    word_set = WordSet.objects.create(
        name="Angielski A1",
        description="Podstawowe słówka",
        level="A1",
        image="default.jpg",
        slug="angielski-a1",
        is_public=True,
        is_featured=False,
        is_deleted=False,
        is_favorite=False,
        owner=user_1,
    )
    StudySession.objects.create(
        user=user_1,
        word_set=word_set,
    )
    StudySession.objects.create(
        user=user_2,
        word_set=word_set,
    )

    assert get_completed_sessions(user_1) == 1


@pytest.mark.django_db
def test_get_current_streak_returns_one_when_user_studied_today(django_user_model):
    user = django_user_model.objects.create_user(username="jan", password="haslo")
    word_set = WordSet.objects.create(
        name="Angielski A1",
        description="Podstawowe słówka",
        level="A1",
        image="default.jpg",
        slug="angielski-a1",
        is_public=True,
        is_featured=False,
        is_deleted=False,
        is_favorite=False,
        owner=user,
    )
    StudySession.objects.create(
        user=user,
        word_set=word_set,
    )

    assert get_current_streak(user) == 1


@pytest.mark.django_db
def test_get_current_streak_returns_zero_when_user_has_no_sessions(django_user_model):
    user = django_user_model.objects.create_user(username="jan", password="haslo")

    assert get_current_streak(user) == 0


@pytest.mark.django_db
def test_get_current_streak_returns_one_when_user_studied_yesterday(django_user_model):
    user = django_user_model.objects.create_user(username="jan", password="haslo")
    word_set = WordSet.objects.create(
        name="Angielski A1",
        description="Podstawowe słówka",
        level="A1",
        image="default.jpg",
        slug="angielski-a1",
        is_public=True,
        is_featured=False,
        is_deleted=False,
        is_favorite=False,
        owner=user,
    )
    study_session = StudySession.objects.create(
        user=user,
        word_set=word_set,
    )
    StudySession.objects.filter(pk=study_session.pk).update(
        created_at=timezone.now() - timedelta(days=1)
    )

    assert get_current_streak(user) == 1


@pytest.mark.django_db
def test_get_current_streak_returns_two_when_user_studied_today_and_yesterday(django_user_model):
    user = django_user_model.objects.create_user(username="jan", password="haslo")
    word_set = WordSet.objects.create(
        name="Angielski A1",
        description="Podstawowe słówka",
        level="A1",
        image="default.jpg",
        slug="angielski-a1",
        is_public=True,
        is_featured=False,
        is_deleted=False,
        is_favorite=False,
        owner=user,
    )
    StudySession.objects.create(
        user=user,
        word_set=word_set,
    )
    study_session = StudySession.objects.create(
        user=user,
        word_set=word_set,
    )
    StudySession.objects.filter(pk=study_session.pk).update(
        created_at=timezone.now() - timedelta(days=1)
    )

    assert get_current_streak(user) == 2


@pytest.mark.django_db
def test_get_current_streak_returns_zero_when_user_studied_two_days_ago(django_user_model):
    user = django_user_model.objects.create_user(username="jan", password="haslo")
    word_set = WordSet.objects.create(
        name="Angielski A1",
        description="Podstawowe słówka",
        level="A1",
        image="default.jpg",
        slug="angielski-a1",
        is_public=True,
        is_featured=False,
        is_deleted=False,
        is_favorite=False,
        owner=user,
    )
    study_session = StudySession.objects.create(
        user=user,
        word_set=word_set,
    )
    StudySession.objects.filter(pk=study_session.pk).update(
        created_at=timezone.now() - timedelta(days=2)
    )

    assert get_current_streak(user) == 0


@pytest.mark.django_db
def test_get_current_streak_returns_three_for_three_consecutive_days(django_user_model):
    user = django_user_model.objects.create_user(username="jan", password="haslo")
    word_set = WordSet.objects.create(
        name="Angielski A1",
        description="Podstawowe słówka",
        level="A1",
        image="default.jpg",
        slug="angielski-a1",
        is_public=True,
        is_featured=False,
        is_deleted=False,
        is_favorite=False,
        owner=user,
    )
    study_session_1 = StudySession.objects.create(
        user=user,
        word_set=word_set,
    )
    study_session_2 = StudySession.objects.create(
        user=user,
        word_set=word_set,
    )
    study_session_3 = StudySession.objects.create(
        user=user,
        word_set=word_set,
    )
    StudySession.objects.filter(pk=study_session_2.pk).update(
        created_at=timezone.now() - timedelta(days=1)
    )
    StudySession.objects.filter(pk=study_session_3.pk).update(
        created_at=timezone.now() - timedelta(days=2)
    )
    assert get_current_streak(user) == 3


@pytest.mark.django_db
def test_get_current_streak_counts_multiple_sessions_on_same_day_once(django_user_model):
    user = django_user_model.objects.create_user(username="jan", password="haslo")
    word_set = WordSet.objects.create(
        name="Angielski A1",
        description="Podstawowe słówka",
        level="A1",
        image="default.jpg",
        slug="angielski-a1",
        is_public=True,
        is_featured=False,
        is_deleted=False,
        is_favorite=False,
        owner=user,
    )
    StudySession.objects.create(
        user=user,
        word_set=word_set,
    )
    StudySession.objects.create(
        user=user,
        word_set=word_set,
    )

    assert get_current_streak(user) == 1