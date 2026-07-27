from django.core.exceptions import ValidationError

from words.models import WordSet, Word, StudySession
from django.contrib.auth.models import User

import pytest


def test_word_set_str():
    word_set = WordSet(
        name="Angielski A1",
        description="Podstawowe słówka",
        level="A1",
        image="default.jpg",
        slug="angielski-a1",
    )

    assert str(word_set) == "Angielski A1"


def test_word_set_default_flags():
    word_set = WordSet(
        name="Angielski A1",
        description="Podstawowe słówka",
        level="A1",
        image="default.jpg",
        slug="angielski-a1",
    )

    assert word_set.is_public is False
    assert word_set.is_favorite is False
    assert word_set.is_deleted is False
    assert word_set.is_featured is False


def test_word_set_default_icon():
    word_set = WordSet(
        name="Angielski A1",
        description="Podstawowe słówka",
        level="A1",
        image="default.jpg",
        slug="angielski-a1",
    )
    assert word_set.icon == "bi-journal-bookmark"
    assert word_set.icon_color == "stat-green"


@pytest.mark.django_db
def test_word_set_can_be_saved_to_database():
    WordSet.objects.create(
        name="Angielski A1",
        description="Podstawowe słówka",
        level="A1",
        image="default.jpg",
        slug="angielski-a1",
    )

    assert WordSet.objects.count() == 1

    saved_word_set = WordSet.objects.get()
    assert saved_word_set.name == "Angielski A1"


@pytest.mark.django_db
def test_word_set_owner():
    user = User.objects.create_user(
        username="jan",
        password="haslo",
    )

    WordSet.objects.create(
        name="Angielski A1",
        description="Podstawowe słówka",
        level="A1",
        image="default.jpg",
        slug="angielski-a1",
        owner=user
    )

    saved_word_set = WordSet.objects.get()
    assert saved_word_set.owner.username == "jan"


def test_word_str():
    word = Word(
        text_pl="drzewo",
        text_en="tree",
    )

    assert str(word) == "drzewo - tree"


@pytest.mark.django_db
def test_word_word_set():
    word_set = WordSet.objects.create(
        name="Angielski A1",
        description="Podstawowe słówka",
        level="A1",
        image="default.jpg",
        slug="angielski-a1",
    )

    Word.objects.create(
        text_pl="drzewo",
        text_en="tree",
        word_set=word_set,
    )

    save_word = Word.objects.get()
    assert save_word.word_set.name == "Angielski A1"


@pytest.mark.django_db
def test_word_set_word():
    word_set = WordSet.objects.create(
        name="Angielski A1",
        description="Podstawowe słówka",
        level="A1",
        image="default.jpg",
        slug="angielski-a1",
    )

    Word.objects.create(
        text_pl="drzewo",
        text_en="tree",
        word_set=word_set,
    )

    Word.objects.create(
        text_pl="dom",
        text_en="house",
        word_set=word_set,
    )

    assert word_set.words.count() == 2


@pytest.mark.django_db
def test_study_session_str():
    word_set = WordSet.objects.create(
        name="Angielski A1",
        description="Podstawowe słówka",
        level="A1",
        image="default.jpg",
        slug="angielski-a1",
    )

    user = User.objects.create_user(
        username="jan",
        password="haslo",
    )

    study_session = StudySession.objects.create(
        user=user,
        word_set=word_set,
        success_rate=100
    )

    assert str(study_session) == f"{user.username} - {word_set.name} - 100%"


@pytest.mark.django_db
def test_study_session_default_values():
    user = User.objects.create_user(
        username="jan",
        password="haslo",
    )

    word_set = WordSet.objects.create(
        name="Angielski A1",
        description="Podstawowe słówka",
        level="A1",
        image="default.jpg",
        slug="angielski-a1",
    )

    study_session = StudySession.objects.create(
        user=user,
        word_set=word_set
    )

    assert study_session.correct_answers == 0
    assert study_session.wrong_answers == 0
    assert study_session.success_rate == 0


def test_word_level_cannot_be_lower_than_one():
    word = Word(
        text_pl="drzewo",
        text_en="tree",
        level=0,
    )

    with pytest.raises(ValidationError):
        word.full_clean()


def test_word_level_cannot_be_higher_than_five():
    word = Word(
        text_pl="drzewo",
        text_en="tree",
        level=6,
    )

    with pytest.raises(ValidationError):
        word.full_clean()


def test_word_level_accepts_valid_value():
    word = Word(
        text_pl="drzewo",
        text_en="tree",
        level=2,
    )

    word.full_clean()


@pytest.mark.django_db
def test_deleting_word_set_deletes_related_words_and_study_sessions(django_user_model):
    user = django_user_model.objects.create_user(username="jan", password="haslo",)
    word_set = WordSet.objects.create(
        name="Angielski A1",
        description="Podstawowe słówka",
        level="A1",
        image="default.jpg",
        slug="angielski-a1",
        is_public=False,
        is_featured=False,
        is_deleted=False,
        is_favorite=False,
        owner=user,
    )
    word = Word.objects.create(
        word_set=word_set,
        text_pl="drzewo",
        text_en="tree",
        level=2,
    )
    study_session = StudySession.objects.create(
        user=user,
        word_set=word_set
    )

    word_set.delete()
    assert not Word.objects.filter(id=word.id).exists()
    assert not StudySession.objects.filter(id=study_session.id).exists()