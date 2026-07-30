from pytest_django.asserts import assertTemplateUsed


def test_with_client(client):
    response = client.get("/")

    assert response.status_code == 200


def test_should_use_correct_template_to_render_a_view(client):
    response = client.get("/")
    assertTemplateUsed(response, "words/home.html")
