from django.shortcuts import render
from words.models import Word


def index(request):

    result = ""

    if request.method == "POST":

        word_id = request.POST.get("word_id")
        word = Word.objects.get(id=word_id)

        answer = request.POST.get("answer")

        if word.text_en.lower() == answer.lower():
            result = "Dobrze"
        else:
            result = f"Błąd. Poprawna odpowiedź: {word.text_en}"

        word_new = Word.objects.order_by("?").first()

        while word_new.id == word.id and Word.objects.count() > 1:
            word_new = Word.objects.order_by("?").first()

        word = word_new

    else:
        word = Word.objects.order_by("?").first()

    return render(
        request,
        "words/index.html",
        {
            "word": word,
            "result": result
        }
    )
