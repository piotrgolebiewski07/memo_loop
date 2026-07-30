import pytest
from django.urls import reverse
from pytest_django.asserts import assertContains, assertNotContains
from words.models import WordSet, Word


def test_anonymous_user_is_redirected_from_my_set_detail(client):
    url = reverse("my_set_detail", kwargs={"slug": "angielski-a1"})
    response = client.get(url)

    assert response.status_code == 302
    assert response.url.startswith(reverse("login"))
    assert "next" in response.url


@pytest.mark.django_db
def test_owner_can_access_my_set_detail(client, django_user_model):
    user = django_user_model.objects.create_user(username="jan", password="haslo")
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

    client.force_login(user)
    url = reverse("my_set_detail", kwargs={"slug": word_set.slug})
    response = client.get(url)

    assert response.status_code == 200


@pytest.mark.django_db
def test_other_user_cannot_access_my_set_detail(client, django_user_model):
    user_1 = django_user_model.objects.create_user(username="jan", password="haslo")
    user_2 = django_user_model.objects.create_user(username="adam", password="haslo")
    client.force_login(user_2)
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
        owner=user_1,
    )

    url = reverse("my_set_detail", kwargs={"slug": word_set.slug})
    response = client.get(url)

    assert response.status_code == 404


@pytest.mark.django_db
def test_owner_cannot_access_deleted_my_set_detail(client, django_user_model):
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
        is_deleted=True,
        is_favorite=False,
        owner=user,
    )

    url = reverse("my_set_detail", kwargs={"slug": word_set.slug})
    response = client.get(url)

    assert response.status_code == 404


@pytest.mark.django_db
def test_my_set_detail_displays_set_name_and_its_words(client, django_user_model):
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

    word = Word.objects.create(
        text_pl="drzewo",
        text_en="tree",
        word_set=word_set,
    )

    url = reverse("my_set_detail", kwargs={"slug": word_set.slug})
    response = client.get(url)

    assert response.status_code == 200
    assertContains(response, "drzewo")
    assertContains(response, "tree")
    assertContains(response, word_set.name)


@pytest.mark.django_db
def test_my_set_detail_does_not_display_words_from_another_set(client, django_user_model):
    user = django_user_model.objects.create_user(username="jan", password="haslo")
    client.force_login(user)
    word_set_1 = WordSet.objects.create(
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
    word_set_2 = WordSet.objects.create(
        name="Niemiecki B1",
        description="Podstawowe słówka z niemieckiego",
        level="B1",
        image="czas_wolny.png",
        slug="niemiecki-b1",
        is_public=False,
        is_featured=False,
        is_deleted=False,
        is_favorite=False,
        owner=user,
    )
    word_1 = Word.objects.create(
        text_pl="drzewo",
        text_en="tree",
        word_set=word_set_1,
    )
    word_2 = Word.objects.create(
        text_pl="dom",
        text_en="house",
        word_set=word_set_2,
    )
    url = reverse("my_set_detail", kwargs={"slug": word_set_1.slug})
    response = client.get(url)

    assertContains(response, "drzewo")
    assertNotContains(response, "dom")


@pytest.mark.django_db
def test_owner_can_add_word_to_my_set_detail(client, django_user_model):
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
    url = reverse("my_set_detail", kwargs={"slug": word_set.slug})
    response = client.post(
        url,
        {
            "text_pl": "drzewo",
            "text_en": "tree",
        }
    )

    assert response.status_code == 302
    assert Word.objects.filter(
        text_pl="drzewo",
        text_en="tree",
        word_set=word_set
    ).exists()


@pytest.mark.django_db
def test_owner_cannot_add_word_with_empty_fields(client, django_user_model):
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
    url = reverse("my_set_detail", kwargs={"slug": word_set.slug})
    response = client.post(
        url,
        {
            "text_pl": "",
            "text_en": "",
        }
    )

    assert response.status_code == 200
    assertContains(response, "Uzupełnij oba pola przed dodaniem słówka")
    assert Word.objects.filter(word_set=word_set).count() == 0


@pytest.mark.django_db
def test_owner_cannot_add_duplicate_word_to_my_set_detail(client, django_user_model):
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
    url = reverse("my_set_detail", kwargs={"slug": word_set.slug})
    Word.objects.create(
        text_pl="drzewo",
        text_en="tree",
        word_set=word_set,
    )

    response = client.post(
        url,
        {
            "text_pl": "drzewo",
            "text_en": "tree",
        }
    )

    assert response.status_code == 200
    assertContains(response, "Takie słówko już istnieje w tym zestawie")
    assert Word.objects.filter(word_set=word_set).count() == 1


@pytest.mark.django_db
def test_owner_can_edit_word_in_my_set_detail(client, django_user_model):
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
    url = reverse("my_set_detail", kwargs={"slug": word_set.slug})
    word = Word.objects.create(
        text_pl="drzewo",
        text_en="tree",
        word_set=word_set,
    )

    response = client.post(
        url,
        {
            "text_pl": "drzewo",
            "text_en": "a tree",
            "edit_word_id": word.id,
        }
    )

    assert response.status_code == 302
    word.refresh_from_db()
    assert word.text_pl == "drzewo"
    assert word.text_en == "a tree"


@pytest.mark.django_db
def test_owner_cannot_edit_word_to_duplicate_in_my_set_detail(client, django_user_model):
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
    url = reverse("my_set_detail", kwargs={"slug": word_set.slug})
    word_1 = Word.objects.create(
        text_pl="drzewo",
        text_en="tree",
        word_set=word_set,
    )
    word_2 = Word.objects.create(
        text_pl="dom",
        text_en="house",
        word_set=word_set,
    )
    response = client.post(
        url,
        {
            "text_pl": "drzewo",
            "text_en": "tree",
            "edit_word_id": word_2.id,
        }
    )

    assert response.status_code == 200
    word_2.refresh_from_db()
    assertContains(response, "Takie słówko już istnieje w tym zestawie")
    assert word_2.text_pl == "dom"
    assert word_2.text_en == "house"


@pytest.mark.django_db
def test_owner_can_delete_selected_word_from_my_set_detail(client, django_user_model):
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
    url = reverse("my_set_detail", kwargs={"slug": word_set.slug})
    word_1 = Word.objects.create(
        text_pl="drzewo",
        text_en="tree",
        word_set=word_set,
    )
    word_2 = Word.objects.create(
        text_pl="dom",
        text_en="house",
        word_set=word_set,
    )
    response = client.post(
        url,
        {
            "delete_words": "",
            "selected_words": [word_2.id],
        }
    )

    assert response.status_code == 302
    assert not Word.objects.filter(id=word_2.id).exists()
    assert Word.objects.filter(id=word_1.id).exists()


@pytest.mark.django_db
def test_owner_can_update_name_of_my_set(client, django_user_model):
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
    url = reverse("my_set_detail", kwargs={"slug": word_set.slug})
    response = client.post(
        url,
        {
            "update_set_name": "",
            "set_name": "Angielski A2",
        }
    )

    assert response.status_code == 302
    word_set.refresh_from_db()
    assert word_set.name == "Angielski A2"
    assert word_set.slug == "angielski-a2"


@pytest.mark.django_db
def test_owner_cannot_update_set_name_to_duplicate(client, django_user_model):
    user = django_user_model.objects.create_user(username="jan", password="haslo")
    client.force_login(user)
    word_set_1 = WordSet.objects.create(
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
    word_set_2 = WordSet.objects.create(
        name="Niemiecki B1",
        description="Podstawowe słówka z niemieckiego",
        level="B1",
        image="czas_wolny.png",
        slug="niemiecki-b1",
        is_public=False,
        is_featured=False,
        is_deleted=False,
        is_favorite=False,
        owner=user,
    )
    url = reverse("my_set_detail", kwargs={"slug": word_set_2.slug})
    response = client.post(
        url,
        {
            "update_set_name": "",
            "set_name": "Angielski A1",
        }
    )

    assert response.status_code == 200
    assertContains(response, "Zestaw o takiej nazwie już istnieje")
    word_set_2.refresh_from_db()
    assert word_set_1.name == "Angielski A1"
    assert word_set_2.name == "Niemiecki B1"
    assert word_set_2.slug == "niemiecki-b1"


@pytest.mark.django_db
def test_owner_can_open_word_edit_form_in_my_set_detail(client, django_user_model):
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
    word = Word.objects.create(
        text_pl="drzewo",
        text_en="tree",
        word_set=word_set,
    )

    url = reverse("my_set_detail", kwargs={"slug": word_set.slug}, query={"edit_word": word.id})
    response = client.get(url)

    assert response.status_code == 200
    assert response.context["edit_word"].id == word.id


@pytest.mark.django_db
def test_owner_can_update_set_name_used_by_another_user(client, django_user_model):
    user_1 = django_user_model.objects.create_user(username="jan", password="haslo")
    user_2 = django_user_model.objects.create_user(username="adam", password="haslo")
    client.force_login(user_1)
    word_set_1 = WordSet.objects.create(
        name="Angielski A1",
        description="Podstawowe słówka",
        level="A1",
        image="czas_wolny.png",
        slug="angielski-a1",
        is_public=False,
        is_featured=False,
        is_deleted=False,
        is_favorite=False,
        owner=user_1,
    )
    word_set_2 = WordSet.objects.create(
        name="Niemiecki B1",
        description="Podstawowe słówka z niemieckiego",
        level="B1",
        image="czas_wolny.png",
        slug="niemiecki-b1",
        is_public=False,
        is_featured=False,
        is_deleted=False,
        is_favorite=False,
        owner=user_2,
    )

    url = reverse("my_set_detail", kwargs={"slug": word_set_1.slug})
    response = client.post(
        url,
        {
            "update_set_name": "",
            "set_name": "Niemiecki B1",
        }
    )

    assert response.status_code == 302

    word_set_1.refresh_from_db()
    assert word_set_1.name == "Niemiecki B1"
    assert word_set_1.slug == "niemiecki-b1-2"


@pytest.mark.django_db
def test_owner_cannot_open_edit_form_for_word_from_another_set(client, django_user_model):
    user = django_user_model.objects.create_user(username="jan", password="haslo")
    client.force_login(user)
    word_set_1 = WordSet.objects.create(
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
    word_set_2 = WordSet.objects.create(
        name="Niemiecki B1",
        description="Podstawowe słówka z niemieckiego",
        level="B1",
        image="czas_wolny.png",
        slug="niemiecki-b1",
        is_public=False,
        is_featured=False,
        is_deleted=False,
        is_favorite=False,
        owner=user,
    )
    word = Word.objects.create(
        text_pl="drzewo",
        text_en="tree",
        word_set=word_set_2,
    )
    url = reverse("my_set_detail", kwargs={"slug": word_set_1.slug})
    response = client.get(f"{url}?edit_word={word.id}")

    assert response.status_code == 404


@pytest.mark.django_db
def test_owner_cannot_edit_word_from_another_set(client, django_user_model):
    user = django_user_model.objects.create_user(username="jan", password="haslo")
    client.force_login(user)
    word_set_1 = WordSet.objects.create(
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
    word_set_2 = WordSet.objects.create(
        name="Niemiecki B1",
        description="Podstawowe słówka z niemieckiego",
        level="B1",
        image="czas_wolny.png",
        slug="niemiecki-b1",
        is_public=False,
        is_featured=False,
        is_deleted=False,
        is_favorite=False,
        owner=user,
    )
    word = Word.objects.create(
        text_pl="drzewo",
        text_en="tree",
        word_set=word_set_2,
    )
    url = reverse("my_set_detail", kwargs={"slug": word_set_1.slug})
    response = client.post(
        url,
        {
            "edit_word_id": word.id,
            "text_pl": "dom",
            "text_en": "house",
        }
    )

    assert response.status_code == 404


@pytest.mark.django_db
def test_owner_cannot_delete_word_from_another_set(client,django_user_model):
    user = django_user_model.objects.create_user(username="jan", password="haslo")
    client.force_login(user)
    word_set_1 = WordSet.objects.create(
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
    word_set_2 = WordSet.objects.create(
        name="Niemiecki B1",
        description="Podstawowe słówka z niemieckiego",
        level="B1",
        image="czas_wolny.png",
        slug="niemiecki-b1",
        is_public=False,
        is_featured=False,
        is_deleted=False,
        is_favorite=False,
        owner=user,
    )
    word = Word.objects.create(
        text_pl="drzewo",
        text_en="tree",
        word_set=word_set_2,
    )
    url = reverse("my_set_detail", kwargs={"slug": word_set_1.slug})
    response = client.post(
        url,
        {
            "delete_words": "",
            "selected_words": word.id,
        }
    )

    assert response.status_code == 302
    assert Word.objects.filter(id=word.id, word_set=word_set_2,).exists()


@pytest.mark.django_db
def test_owner_cannot_update_set_name_to_empty_name(client, django_user_model):
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
    url = reverse("my_set_detail", kwargs={"slug": word_set.slug})
    response = client.post(
        url,
        {
            "update_set_name": "",
            "set_name": "",
        }
    )

    assert response.status_code == 200
    assertContains(response, "Podaj nazwę zestawu")

    word_set.refresh_from_db()
    assert word_set.name == "Angielski A1"
