import pytest
from django.urls import reverse
from pytest_django.asserts import assertContains
from words.models import WordSet


def test_anonymous_user_is_redirected_from_create_set(client):
    url = reverse("create_set")
    response = client.get(url)

    assert response.status_code == 302
    assert response.url.startswith(reverse("login"))
    assert "next" in response.url


@pytest.mark.django_db
def test_authenticated_user_can_access_create_set(client, django_user_model):
    user = django_user_model.objects.create_user(username="jan", password="haslo")
    client.force_login(user)
    url = reverse("create_set")
    response = client.get(url)

    assert response.status_code == 200


@pytest.mark.django_db
def test_authenticated_user_can_create_set(client, django_user_model):
    user = django_user_model.objects.create_user(username="jan", password="haslo")
    client.force_login(user)

    url = reverse("create_set")
    response = client.post(
        url,
        {
            "name": "Angielski A1",
        }
    )

    assert response.status_code == 302
    assert WordSet.objects.filter(
        name="Angielski A1",
        owner=user,
        is_public=False,
    ).exists()


@pytest.mark.django_db
def test_create_set_with_empty_name_shows_validation_message(client, django_user_model):
    user = django_user_model.objects.create_user(username="jan", password="haslo")
    client.force_login(user)
    url = reverse("create_set")
    response = client.post(
        url,
        {
            "name": " ",
        }
    )

    assert response.status_code == 200
    assertContains(response, "Podaj nazwę zestawu")
    assert WordSet.objects.count() == 0


@pytest.mark.django_db
def test_create_set_with_duplicate_name_shows_validation_message(client, django_user_model):
    user = django_user_model.objects.create_user(username="jan", password="haslo")
    client.force_login(user)
    WordSet.objects.create(
        name="Angielski A1",
        description="Podstawowe słówka",
        level="A1",
        image="czas_wolny.png",
        slug="angielski-a1",
        is_public=False,
        is_featured=False,
        is_deleted=False,
        owner=user,
    )

    url = reverse("create_set")
    response = client.post(
        url,
        {
            "name": "Angielski A1",
        }
    )

    assert response.status_code == 200
    assertContains(response, "Zestaw o takiej nazwie już istnieje")
    assert WordSet.objects.count() == 1

