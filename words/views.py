from django.shortcuts import render
from words.models import Word


def index(request):

    result = ""
    num_attempts = request.session.get("num_attempts", 0)

    if request.method == "POST":

        if "end_session" in request.POST:

            if "num_attempts" in request.session:
                del request.session["num_attempts"]

            num_attempts = 0
            word = Word.objects.order_by("?").first()

        else:

            num_attempts += 1
            request.session["num_attempts"] = num_attempts

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
            "result": result,
            'num_attempts': num_attempts
        }
    )
