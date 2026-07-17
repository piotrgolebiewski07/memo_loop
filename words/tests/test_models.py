from words.models import WordSet

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

