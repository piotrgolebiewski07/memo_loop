import pytest

from django.urls import reverse
from pytest_django.asserts import assertContains, assertNotContains
from words.models import WordSet


def test_anonymous_user_is_redirected_from_my_sets(client):
    url = reverse("my_sets")
    response = client.get(url)

    assert response.status_code == 302
    assert response.url.startswith(reverse("login"))
    assert "next" in response.url


@pytest.mark.django_db
def test_authenticated_user_can_access_my_sets(client, django_user_model):
    user = django_user_model.objects.create_user(username="jan", password="haslo")
    client.force_login(user)

    url = reverse("my_sets")
    response = client.get(url)

    assert response.status_code == 200


@pytest.mark.django_db
def test_my_sets_displays_only_current_users_sets(client, django_user_model):
    user_1 = django_user_model.objects.create_user(username="jan", password="haslo")
    user_2 = django_user_model.objects.create_user(username="adam", password="haslo")

    WordSet.objects.create(
        name="Angielski A1",
        description="Podstawowe słówka",
        level="A1",
        image="czas_wolny.png",
        slug="angielski-a1",
        is_public=False,
        is_featured=False,
        is_deleted=False,
        owner=user_1,
    )

    WordSet.objects.create(
        name="Niemiecki B1",
        description="Podstawowe słówka niemieckie",
        level="B1",
        image="czas_wolny.png",
        slug="niemiecki-b1",
        is_public=False,
        is_featured=False,
        is_deleted=False,
        owner=user_2,
    )

    client.force_login(user_1)
    url = reverse("my_sets")
    response = client.get(url)

    assertContains(response, "Angielski A1")
    assertNotContains(response, "Niemiecki B1")
    assert response.context["set_count"] == 1


@pytest.mark.django_db
def test_my_sets_does_not_display_deleted_set(client, django_user_model):
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
        is_deleted=True,
        owner=user,
    )

    url = reverse("my_sets")
    response = client.get(url)

    assertNotContains(response, "Angielski A1")
    assert response.context["set_count"] == 0


@pytest.mark.django_db
def test_my_sets_favorites_filter_displays_only_favorite_sets(client, django_user_model):
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
        is_favorite=True,
        owner=user,
    )

    WordSet.objects.create(
        name="Niemiecki B1",
        description="Podstawowe słówka niemieckie",
        level="B1",
        image="czas_wolny.png",
        slug="niemiecki-b1",
        is_public=False,
        is_featured=False,
        is_deleted=False,
        is_favorite=False,
        owner=user,
    )

    url = reverse("my_sets", query={"filter": "favorites"})
    response = client.get(url)

    assertContains(response, "Angielski A1")
    assertNotContains(response, "Niemiecki B1")
    assert response.context["set_count"] == 1


@pytest.mark.django_db
def test_my_sets_search_displays_matching_sets(client, django_user_model):
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
        is_favorite=True,
        owner=user,
    )

    WordSet.objects.create(
        name="Niemiecki B1",
        description="Podstawowe słówka niemieckie",
        level="B1",
        image="czas_wolny.png",
        slug="niemiecki-b1",
        is_public=False,
        is_featured=False,
        is_deleted=False,
        is_favorite=False,
        owner=user,
    )

    url = reverse("my_sets", query={"q": "Angielski"})
    response = client.get(url)
    assertContains(response, "Angielski A1")
    assertNotContains(response, "Niemiecki B1")
    assert response.context["search_query"] == "Angielski"


@pytest.mark.django_db
def test_my_sets_sort_by_name_ascending(client, django_user_model):
    user = django_user_model.objects.create_user(username="jan", password="haslo")
    client.force_login(user)
    WordSet.objects.create(
        name="Niemiecki B1",
        description="Podstawowe słówka niemieckie",
        level="B1",
        image="czas_wolny.png",
        slug="niemiecki-b1",
        is_public=False,
        is_featured=False,
        is_deleted=False,
        is_favorite=False,
        owner=user,
    )
    WordSet.objects.create(
        name="Angielski A1",
        description="Podstawowe słówka",
        level="A1",
        image="czas_wolny.png",
        slug="angielski-a1",
        is_public=False,
        is_featured=False,
        is_deleted=False,
        is_favorite=True,
        owner=user,
    )

    url = reverse("my_sets", query={"sort": "name_asc"})
    response = client.get(url)

    assert response.context["word_sets"][0]["set"].name == "Angielski A1"
    assert response.context["word_sets"][1]["set"].name == "Niemiecki B1"


@pytest.mark.django_db
def test_my_sets_post_toggles_set_as_favorite(client,django_user_model):
    user = django_user_model.objects.create_user(username="jan", password="haslo")
    client.force_login(user)
    word_set = WordSet.objects.create(
        name="Angielski A1",
        description="Podstawowe słówka",
        level="A1",
        image="czas_wolny.png",
        slug="angielski-a1",
        is_public=False,
        is_featured=False,
        is_deleted=False,
        is_favorite=False,
        owner=user,
    )

    url = reverse("my_sets")
    response = client.post(
        url,
        {
            "favorite_set_id": word_set.id,
        }
    )

    assert response.status_code == 302
    word_set.refresh_from_db()
    assert word_set.is_favorite is True


@pytest.mark.django_db
def test_my_sets_post_marks_set_as_deleted(client, django_user_model):
    user = django_user_model.objects.create_user(username="jan", password="haslo")
    client.force_login(user)
    word_set = WordSet.objects.create(
        name="Angielski A1",
        description="Podstawowe słówka",
        level="A1",
        image="czas_wolny.png",
        slug="angielski-a1",
        is_public=False,
        is_featured=False,
        is_deleted=False,
        is_favorite=False,
        owner=user,
    )

    url = reverse("my_sets")
    response = client.post(
        url,
        {
            "delete_set_id": word_set.id,
        }
    )

    assert response.status_code == 302
    word_set.refresh_from_db()
    assert word_set.is_deleted is True


@pytest.mark.django_db
def test_user_cannot_delete_another_users_set(client, django_user_model):
    user_1 = django_user_model.objects.create_user(username="jan", password="haslo")
    user_2 = django_user_model.objects.create_user(username="adam", password="haslo")
    client.force_login(user_2)
    word_set = WordSet.objects.create(
        name="Niemiecki B1",
        description="Podstawowe słówka niemieckie",
        level="B1",
        image="czas_wolny.png",
        slug="niemiecki-b1",
        is_public=False,
        is_featured=False,
        is_deleted=False,
        is_favorite=False,
        owner=user_1,
    )

    url = reverse("my_sets")
    response = client.post(
        url,
        {
            "delete_set_id": word_set.id,
        }
    )

    assert response.status_code == 404
    word_set.refresh_from_db()
    assert word_set.is_deleted is False


@pytest.mark.django_db
def test_user_cannot_toggle_another_users_set_as_favorite(client, django_user_model):
    user_1 = django_user_model.objects.create_user(username="jan", password="haslo")
    user_2 = django_user_model.objects.create_user(username="adam", password="haslo")
    client.force_login(user_2)
    word_set = WordSet.objects.create(
        name="Niemiecki B1",
        description="Podstawowe słówka niemieckie",
        level="B1",
        image="czas_wolny.png",
        slug="niemiecki-b1",
        is_public=False,
        is_featured=False,
        is_deleted=False,
        is_favorite=False,
        owner=user_1,
    )

    url = reverse("my_sets")
    response = client.post(
        url,
        {
            "favorite_set_id": word_set.id,
        }
    )

    assert response.status_code == 404
    word_set.refresh_from_db()
    assert word_set.is_favorite is False

