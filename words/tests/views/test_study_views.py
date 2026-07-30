import pytest

from django.urls import reverse
from pytest_django.asserts import assertContains
from words.models import WordSet, Word, StudySession


@pytest.mark.django_db
def test_anonymous_user_can_access_public_study_set(client):
    word_set = WordSet.objects.create(
        name="Angielski A1",
        description="Podstawowe słówka",
        level="A1",
        image="czas_wolny.png",
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
        image="czas_wolny.png",
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
        image="czas_wolny.png",
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
        image="czas_wolny.png",
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
        image="czas_wolny.png",
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
        image="czas_wolny.png",
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
        image="czas_wolny.png",
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
        image="czas_wolny.png",
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
        image="czas_wolny.png",
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
        image="czas_wolny.png",
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
        image="czas_wolny.png",
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
        image="czas_wolny.png",
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
        image="czas_wolny.png",
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
