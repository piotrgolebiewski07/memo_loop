from django.shortcuts import render
from words.models import Word
from .models import WordSet


def index(request):

    result = ""
    correct_answers = request.session.get("correct_answers", 0)
    wrong_answers = request.session.get("wrong_answers", 0)

    if request.method == "POST":

        if "end_session" in request.POST:

            if "correct_answers" in request.session:
                del request.session["correct_answers"]
            if "wrong_answers" in request.session:
                del request.session["wrong_answers"]

            correct_answers, wrong_answers = 0, 0
            word = Word.objects.order_by("?").first()

        else:

            word_id = request.POST.get("word_id")
            word = Word.objects.get(id=word_id)

            answer = request.POST.get("answer")

            if word.text_en.lower() == answer.lower():
                result = "Dobrze"
                correct_answers += 1
                request.session["correct_answers"] = correct_answers
            else:
                result = f"Błąd. Poprawna odpowiedź: {word.text_en}"
                wrong_answers += 1
                request.session["wrong_answers"] = wrong_answers

            word_new = Word.objects.order_by("?").first()

            while word_new.id == word.id and Word.objects.count() > 1:
                word_new = Word.objects.order_by("?").first()

            word = word_new

    else:
        if "correct_answers" in request.session:
            del request.session["correct_answers"]
        if "wrong_answers" in request.session:
            del request.session["wrong_answers"]

        correct_answers, wrong_answers = 0, 0
        word = Word.objects.order_by("?").first()

    return render(
        request,
        "words/study.html",
        {
            "word": word,
            "result": result,
            'correct_answers': correct_answers,
            'wrong_answers': wrong_answers,
        }
    )


def home(request):
    return render(
        request,
        "words/home.html",
        )


def ready_sets(request):
    word_sets = WordSet.objects.all()

    return render(
        request,
        "words/ready_sets.html",
        {
            "word_sets": word_sets,
        }
    )


def study_set(request, slug):
    result = ""
    correct_answers = request.session.get("correct_answers", 0)
    wrong_answers = request.session.get("wrong_answers", 0)

    word_set = WordSet.objects.get(slug=slug)

    if request.method == "POST":
        word_id = request.POST.get("word_id")
        word = Word.objects.get(id=word_id)

        answer = request.POST.get("answer")

        if word.text_en.lower() == answer.lower():
            result = "Dobrze"
            correct_answers += 1
            request.session["correct_answers"] = correct_answers
        else:
            result = f"Błąd. Poprawna odpowiedź: {word.text_en}"
            wrong_answers += 1
            request.session["wrong_answers"] = wrong_answers

        word_new = word_set.words.order_by("?").first()

        while word_new.id == word.id and word_set.words.count() > 1:
            word_new = word_set.words.order_by("?").first()

        word = word_new

    else:

        if "correct_answers" in request.session:
            del request.session["correct_answers"]
        if "wrong_answers" in request.session:
            del request.session["wrong_answers"]

        correct_answers, wrong_answers = 0, 0
        word = word_set.words.order_by("?").first()

    return render(
        request,
        "words/study.html",
        {
            "word": word,
            "result": result,
            "correct_answers": correct_answers,
            "wrong_answers": wrong_answers,
            "word_set": word_set,
        }
    )
