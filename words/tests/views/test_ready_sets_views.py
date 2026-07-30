import pytest

from django.urls import reverse
from pytest_django.asserts import assertContains, assertNotContains, assertTemplateUsed
from words.models import WordSet, Word, StudySession


@pytest.mark.django_db
def test_ready_sets_page_returns_status_200(client):
    response = client.get("/ready-sets/")

    assert response.status_code == 200


@pytest.mark.django_db
def test_ready_sets_page_uses_correct_template(client):
    response = client.get("/ready-sets/")
    assertTemplateUsed(response, "words/ready_sets.html")


@pytest.mark.django_db
def test_ready_sets_page_displays_featured_public_set(client):
    WordSet.objects.create(
        name="Angielski A1",
        description="Podstawowe słówka",
        level="A1",
        image="czas_wolny.png",
        slug="angielski-a1",
        is_public=True,
        is_featured=True,
        is_deleted=False,
    )

    response = client.get("/ready-sets/")
    assertContains(response, "Angielski A1")


@pytest.mark.django_db
def test_ready_sets_page_does_not_display_non_featured_set(client):
    WordSet.objects.create(
        name="Angielski A1",
        description="Podstawowe słówka",
        level="A1",
        image="czas_wolny.png",
        slug="angielski-a1",
        is_public=True,
        is_featured=False,
        is_deleted=False,
    )

    response = client.get("/ready-sets/")
    assertNotContains(response, "Angielski A1")


@pytest.mark.django_db
def test_ready_sets_page_does_not_display_deleted_set(client):
    WordSet.objects.create(
        name="Angielski A1",
        description="Podstawowe słówka",
        level="A1",
        image="czas_wolny.png",
        slug="angielski-a1",
        is_public=True,
        is_featured=True,
        is_deleted=True,
    )

    response = client.get("/ready-sets/")
    assertNotContains(response, "Angielski A1")


@pytest.mark.django_db
def test_ready_sets_page_displays_non_featured_set_when_show_all_is_true(client):
    WordSet.objects.create(
        name="Angielski A1",
        description="Podstawowe słówka",
        level="A1",
        image="czas_wolny.png",
        slug="angielski-a1",
        is_public=True,
        is_featured=False,
        is_deleted=False,
    )

    response = client.get("/ready-sets/?show-all=true")
    assertContains(response, "Angielski A1")


@pytest.mark.django_db
def test_ready_sets_page_does_not_display_private_set(client):
    WordSet.objects.create(
        name="Angielski C1",
        description="Zaawansowane słówka",
        level="C1",
        image="czas_wolny.png",
        slug="angielski-c1",
        is_public=False,
        is_featured=True,
        is_deleted=False,
    )

    response = client.get("/ready-sets/?show-all=true")
    assert response.status_code == 200
    assertNotContains(response, "Angielski C1")


@pytest.mark.django_db
def test_ready_sets_page_context_contains_public_sets_count(client):
    WordSet.objects.create(
        name="Angielski A1",
        description="Podstawowe słówka",
        level="A1",
        image="czas_wolny.png",
        slug="angielski-a1",
        is_public=True,
        is_featured=False,
        is_deleted=False,
    )

    WordSet.objects.create(
        name="Angielski C1",
        description="Zaawansowane słówka",
        level="C1",
        image="czas_wolny.png",
        slug="angielski-c1",
        is_public=True,
        is_featured=True,
        is_deleted=False,
    )

    response = client.get("/ready-sets/")
    assert response.context["set_count"] == 2

