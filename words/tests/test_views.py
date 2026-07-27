import pytest
from django.urls import reverse
from pytest_django.asserts import assertTemplateUsed, assertContains, assertNotContains, assertTemplateUsed
from words.models import WordSet, Word, StudySession


# --- Home view ---
def test_with_client(client):
    response = client.get("/")

    assert response.status_code == 200


def test_should_use_correct_template_to_render_a_view(client):
    response = client.get("/")
    assertTemplateUsed(response, "words/home.html")


# --- Ready sets view ---
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


@pytest.mark.django_db
def test_ready_sets_page_displays_non_featured_set_when_show_all_is_true(client):
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

    response = client.get("/ready-sets/?show-all=true")
    assertContains(response, "Angielski A1")


@pytest.mark.django_db
def test_ready_sets_page_does_not_display_private_set(client):
    WordSet.objects.create(
        name="Angielski C1",
        description="Zaawansowane słówka",
        level="C1",
        image="default.jpg",
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
        image="default.jpg",
        slug="angielski-a1",
        is_public=True,
        is_featured=False,
        is_deleted=False,
    )

    WordSet.objects.create(
        name="Angielski C1",
        description="Zaawansowane słówka",
        level="C1",
        image="default.jpg",
        slug="angielski-c1",
        is_public=True,
        is_featured=True,
        is_deleted=False,
    )

    response = client.get("/ready-sets/")
    assert response.context["set_count"] == 2


# --- Study set view ---
@pytest.mark.django_db
def test_anonymous_user_can_access_public_study_set(client):
    word_set = WordSet.objects.create(
        name="Angielski A1",
        description="Podstawowe słówka",
        level="A1",
        image="default.jpg",
        slug="angielski-a1",
        is_public=True,
        is_featured=False,
        is_deleted=False,
    )

    url = reverse("study_set", kwargs={"slug": word_set.slug})
    response = client.get(url)

    assert response.status_code == 200


@pytest.mark.django_db
def test_anonymous_user_cannot_access_private_study_set(client):
    word_set = WordSet.objects.create(
        name="Angielski A1",
        description="Podstawowe słówka",
        level="A1",
        image="default.jpg",
        slug="angielski-a1",
        is_public=False,
        is_featured=False,
        is_deleted=False,
    )
    url = reverse("study_set", kwargs={"slug": word_set.slug})
    response = client.get(url)

    assert response.status_code == 404


@pytest.mark.django_db
def test_owner_can_access_private_study_set(client, django_user_model):
    user = django_user_model.objects.create_user(username="jan", password="haslo")

    word_set = WordSet.objects.create(
        name="Angielski A1",
        description="Podstawowe słówka",
        level="A1",
        image="default.jpg",
        slug="angielski-a1",
        is_public=False,
        is_featured=False,
        is_deleted=False,
        owner=user,
    )

    client.force_login(user)
    url = reverse("study_set", kwargs={"slug": word_set.slug})

    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_other_user_cannot_access_private_study_set(client, django_user_model):
    user_1 = django_user_model.objects.create_user(username="jan", password="haslo")
    user_2 = django_user_model.objects.create_user(username="adam", password="haslo")

    word_set = WordSet.objects.create(
        name="Angielski A1",
        description="Podstawowe słówka",
        level="A1",
        image="default.jpg",
        slug="angielski-a1",
        is_public=False,
        is_featured=False,
        is_deleted=False,
        owner=user_1,
    )

    client.force_login(user_2)
    url = reverse("study_set", kwargs={"slug": word_set.slug})

    response = client.get(url)
    assert response.status_code == 404


@pytest.mark.django_db
def test_public_study_set_displays_word(client):
    word_set = WordSet.objects.create(
        name="Angielski A1",
        description="Podstawowe słówka",
        level="A1",
        image="default.jpg",
        slug="angielski-a1",
        is_public=True,
        is_featured=False,
        is_deleted=False,
    )

    word = Word.objects.create(
        text_pl="drzewo",
        text_en="tree",
        word_set=word_set,
    )

    url = reverse("study_set", kwargs={"slug": word_set.slug})
    response = client.get(url)

    assert response.status_code == 200
    assertContains(response, word.text_pl)


@pytest.mark.django_db
def test_public_study_set_shows_success_message_for_correct_answer(client):
    word_set = WordSet.objects.create(
        name="Angielski A1",
        description="Podstawowe słówka",
        level="A1",
        image="default.jpg",
        slug="angielski-a1",
        is_public=True,
        is_featured=False,
        is_deleted=False,
    )

    word = Word.objects.create(
        text_pl="drzewo",
        text_en="tree",
        word_set=word_set,
    )

    url = reverse("study_set", kwargs={"slug": word_set.slug})
    client.get(url)
    response = client.post(
        url,
        {
            "word_id": word.id,
            "answer": word.text_en,
        },
    )

    assert response.status_code == 200
    assertContains(response, "SUPER!")


@pytest.mark.django_db
def test_public_study_set_displays_summary_after_clicking_next_word(client):
    word_set = WordSet.objects.create(
        name="Angielski A1",
        description="Podstawowe słówka",
        level="A1",
        image="default.jpg",
        slug="angielski-a1",
        is_public=True,
        is_featured=False,
        is_deleted=False,
    )

    word = Word.objects.create(
        text_pl="drzewo",
        text_en="tree",
        word_set=word_set,
    )

    url = reverse("study_set", kwargs={"slug": word_set.slug})
    client.get(url)
    response_after_answer = client.post(
        url,
        {
            "word_id": word.id,
            "answer": word.text_en,
        },
    )

    assertContains(response_after_answer, "SUPER!")

    response = client.post(
        url,
        {
            "next_word": "",
        },
    )

    assert response.status_code == 200
    assertContains(response, "Idealnie!")


@pytest.mark.django_db
def test_completed_private_study_session_is_saved(client, django_user_model):
    user = django_user_model.objects.create_user(username="adam", password="haslo")
    word_set = WordSet.objects.create(
        name="Angielski A1",
        description="Podstawowe słówka",
        level="A1",
        image="default.jpg",
        slug="angielski-a1",
        is_public=False,
        is_featured=False,
        is_deleted=False,
        owner=user,
    )

    word = Word.objects.create(
        text_pl="drzewo",
        text_en="tree",
        word_set=word_set,
    )

    client.force_login(user)
    url = reverse("study_set", kwargs={"slug": word_set.slug})
    response = client.get(url)
    assertContains(response, word.text_pl)
    client.post(
        url,
        {
            "word_id": word.id,
            "answer": word.text_en,
        },
    )

    client.post(
        url,
        {
            "next_word": "",
        },
    )

    assert StudySession.objects.filter(user=user, word_set=word_set).count() == 1

    study_session = StudySession.objects.get(
        user=user,
        word_set=word_set,
    )

    assert study_session.correct_answers == 1
    assert study_session.wrong_answers == 0
    assert study_session.success_rate == 100


@pytest.mark.django_db
def test_public_study_set_shows_correct_answer_after_wrong_answer(client):
    word_set = WordSet.objects.create(
        name="Angielski A1",
        description="Podstawowe słówka",
        level="A1",
        image="default.jpg",
        slug="angielski-a1",
        is_public=True,
        is_featured=False,
        is_deleted=False,
    )

    word = Word.objects.create(
        text_pl="drzewo",
        text_en="tree",
        word_set=word_set,
    )

    url = reverse("study_set", kwargs={"slug": word_set.slug})
    client.get(url)
    response = client.post(
        url,
        {
            "word_id": word.id,
            "answer": "three"
        },
    )

    assert response.status_code == 200
    assertContains(response, word.text_en)
    assert response.context["wrong_answers"] == 1


@pytest.mark.django_db
def test_wrong_answer_returns_word_to_study_queue(client):
    word_set = WordSet.objects.create(
        name="Angielski A1",
        description="Podstawowe słówka",
        level="A1",
        image="default.jpg",
        slug="angielski-a1",
        is_public=True,
        is_featured=False,
        is_deleted=False,
    )

    word = Word.objects.create(
        text_pl="drzewo",
        text_en="tree",
        word_set=word_set,
    )

    url = reverse("study_set", kwargs={"slug": word_set.slug})
    client.get(url)
    response = client.post(
        url,
        {
            "word_id": word.id,
            "answer": "three",
        }
    )

    session = client.session
    session_key = f"study_words_{word_set.id}"

    assert session[session_key] == [word.id]


@pytest.mark.django_db
def test_ending_public_study_redirects_to_ready_sets(client):
    word_set = WordSet.objects.create(
        name="Angielski A1",
        description="Podstawowe słówka",
        level="A1",
        image="default.jpg",
        slug="angielski-a1",
        is_public=True,
        is_featured=False,
        is_deleted=False,
    )

    url = reverse("study_set", kwargs={"slug": word_set.slug})
    client.get(url)

    response = client.post(
        url,
        {
            "end_study": "",
        }
    )

    assert response.status_code == 302
    assert response.url == reverse("ready_sets")


@pytest.mark.django_db
def test_ending_private_study_redirects_to_my_sets_with_filter(client, django_user_model):
    user = django_user_model.objects.create_user(username="jan", password="haslo")
    word_set = WordSet.objects.create(
        name="Angielski A1",
        description="Podstawowe słówka",
        level="A1",
        image="default.jpg",
        slug="angielski-a1",
        is_public=False,
        is_featured=False,
        is_deleted=False,
        owner=user,
    )
    client.force_login(user)
    url = reverse("study_set", kwargs={"slug": word_set.slug}, query={"filter": "favorites"})
    client.get(url)

    response = client.post(
        url,
        {
            "end_study": "",
        }
    )

    assert response.status_code == 302
    assert response.url == reverse("my_sets", query={"filter": "favorites"})


@pytest.mark.django_db
def test_study_set_displays_summary_when_word_set_is_empty(client, django_user_model):
    user = django_user_model.objects.create_user(username="jan", password="haslo")
    client.force_login(user)
    word_set = WordSet.objects.create(
        name="Angielski A1",
        description="Podstawowe słówka",
        level="A1",
        image="default.jpg",
        slug="angielski-a1",
        is_public=False,
        is_featured=False,
        is_deleted=False,
        owner=user,
    )
    url = reverse("study_set", kwargs={"slug": word_set.slug})
    response = client.get(url)

    assert response.status_code == 200
    assertContains(response, "Gratulacje")


# --- Create set view ---
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
        image="default.jpg",
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


# --- My sets view ---
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
        image="default.jpg",
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
        image="default.jpg",
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
        image="default.jpg",
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
        image="default.jpg",
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
        image="default.jpg",
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
        image="default.jpg",
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
        image="default.jpg",
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
        image="default.jpg",
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
        image="default.jpg",
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
        image="default.jpg",
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
        image="default.jpg",
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
        image="default.jpg",
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
        image="default.jpg",
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


# --- My sets detail view ---
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
        image="default.jpg",
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
        image="default.jpg",
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
        image="default.jpg",
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
        image="default.jpg",
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
        image="default.jpg",
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
        image="default.jpg",
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
        image="default.jpg",
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
        image="default.jpg",
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
        image="default.jpg",
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
        image="default.jpg",
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
        image="default.jpg",
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
        image="default.jpg",
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
        image="default.jpg",
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
        image="default.jpg",
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
        image="default.jpg",
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
        image="default.jpg",
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
        image="default.jpg",
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
        image="default.jpg",
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
        image="default.jpg",
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
        image="default.jpg",
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
        image="default.jpg",
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
        image="default.jpg",
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


# --- Authentication views ---
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
