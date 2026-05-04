from django.http import HttpResponse
from django.shortcuts import render
from words.models import Word


def index(request):
    word = Word.objects.order_by("?")[0]

    return render(
        request,
        "words/index.html",
        {"word": word}
    )

