from django.shortcuts import render, redirect
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
    result_class = ""
    correct_answers = request.session.get("correct_answers", 0)
    wrong_answers = request.session.get("wrong_answers", 0)

    word_set = WordSet.objects.get(slug=slug)

    if request.method == "POST":

        if "end_study" in request.POST:
            request.session.pop("correct_answers", None)
            request.session.pop("wrong_answers", None)

            return redirect("/ready-sets/")

        if "end_session" in request.POST:
            if "correct_answers" in request.session:
                del request.session["correct_answers"]
            if "wrong_answers" in request.session:
                del request.session["wrong_answers"]

            correct_answers, wrong_answers = 0, 0
            result = ""
            word = word_set.words.order_by("?").first()

        else:
            word_id = request.POST.get("word_id")
            word = Word.objects.get(id=word_id)

            answer = request.POST.get("answer")

            if word.text_en.lower() == answer.lower():
                result = "SUPER!"
                result_class = "success"
                correct_answers += 1
                request.session["correct_answers"] = correct_answers
            else:
                result = f"{word.text_en}"
                result_class = "danger"
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

    total_answers = correct_answers + wrong_answers

    if total_answers > 0:
        success_rate = round((correct_answers / total_answers) * 100)
    else:
        success_rate = 0

    return render(
        request,
        "words/study.html",
        {
            "word": word,
            "result": result,
            "correct_answers": correct_answers,
            "wrong_answers": wrong_answers,
            "word_set": word_set,
            "success_rate": success_rate,
            "result_class": result_class,
        }
    )


def my_sets(request):

    return render(
        request,
        "words/my_sets.html",
    )


def create_set(request):
    return render(
        request,
        "words/create_set.html",
    )


def my_set_detail(request, slug):
    word_set = WordSet.objects.get(slug=slug)

    return render(
        request,
        "words/my_set_detail.html",
        {
            "word_set": word_set,
        }
    )

