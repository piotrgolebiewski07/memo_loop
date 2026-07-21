import pytest
from pytest_django.asserts import assertTemplateUsed, assertContains, assertNotContains
from words.models import WordSet


def test_with_client(client):
    response = client.get("/")

    assert response.status_code == 200


def test_should_use_correct_template_to_render_a_view(client):
    response = client.get("/")
    assertTemplateUsed(response, "words/home.html")


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
        image="default.jpg",
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
        image="default.jpg",
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
        image="default.jpg",
        slug="angielski-a1",
        is_public=True,
        is_featured=True,
        is_deleted=True,
    )

    response = client.get("/ready-sets/")
    assertNotContains(response, "Angielski A1")
