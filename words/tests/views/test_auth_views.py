import pytest
from django.urls import reverse
from pytest_django.asserts import assertTemplateUsed


def test_register_page_returns_status_200(client):
    url = reverse("register")
    response = client.get(url)

    assert response.status_code == 200


def test_register_page_uses_correct_template(client):
    url = reverse("register")
    response = client.get(url)

    assertTemplateUsed(response, "registration/register.html")


@pytest.mark.django_db
def test_user_can_register(client, django_user_model):
    url = reverse("register")
    response = client.post(
        url,
        {
            "username": "jan",
            "password1": "HasloDoTestu123!",
            "password2": "HasloDoTestu123!",
        }
    )

    assert response.status_code == 302
    assert django_user_model.objects.filter(username="jan").exists()
    assert response.url == reverse("home")


@pytest.mark.django_db
def test_user_cannot_register_with_mismatched_passwords(client, django_user_model):
    url = reverse("register")
    response = client.post(
        url,
        {
            "username": "jan",
            "password1": "HasloDoTestu123!",
            "password2": "HasloDoTestu111!",
        }
    )

    assert response.status_code == 200
    assert not django_user_model.objects.filter(username="jan").exists()


@pytest.mark.django_db
def test_user_cannot_register_with_existing_username(client, django_user_model):
    user = django_user_model.objects.create_user(username="jan", password="haslo")
    url = reverse("register")
    response = client.post(
        url,
        {
            "username": "jan",
            "password1": "HasloDoTestu123!",
            "password2": "HasloDoTestu123!",
        }
    )

    assert response.status_code == 200
    assert django_user_model.objects.filter(username="jan").count() == 1


def test_user_is_logged_in_after_registration(client, django_user_model):
    url = reverse("register")
    client.post(
        url,
        {
            "username": "jan",
            "password1": "HasloDoTestu123!",
            "password2": "HasloDoTestu123!",
        }
    )
    response = client.get(reverse("create_set"))

    assert response.status_code == 200


@pytest.mark.django_db
def test_login_redirects_user_to_next_url(client, django_user_model):
    django_user_model.objects.create_user(username="jan", password="haslo")
    url = reverse("create_set")

    response = client.get(url)
    assert response.status_code == 302
    assert "next" in response.url

    login_url = response.url

    response = client.post(
        login_url,
        {
            "username": "jan",
            "password": "haslo",
        },
    )

    assert response.status_code == 302
    assert response.url == url


@pytest.mark.django_db
def test_user_cannot_login_with_invalid_password(client, django_user_model):
    django_user_model.objects.create_user(username="jan", password="haslo")
    url = reverse("login")
    response = client.post(
        url,
        {
            "username": "jan",
            "password": "haslo1",
        },
    )

    assert response.status_code == 200
    response = client.get(reverse("create_set"))
    assert response.status_code == 302


@pytest.mark.django_db
def test_authenticated_user_can_logout(client, django_user_model):
    user = django_user_model.objects.create_user(username="jan", password="haslo")
    client.force_login(user)
    url = reverse("logout")
    response = client.post(url)

    assert response.status_code == 302
    assert response.url == reverse("home")

    response = client.get(reverse("create_set"))

    assert response.status_code == 302
