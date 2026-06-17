from django.shortcuts import render, redirect
from django.utils.text import slugify
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login

from words.models import Word
from .models import WordSet

import random


def word_count_label(count):
    if count == 1:
        return "słówko"
    if count % 10 in [2, 3, 4] and count % 100 not in [12, 13, 14]:
        return "słówka"
    return "słówek"


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
    word_sets = WordSet.objects.filter(is_public=True)

    ready_word_sets = []

    for word_set in word_sets:
        word_count = word_set.words.count()

        ready_word_sets.append({
            "set": word_set,
            "word_count": word_count,
            "word_label": word_count_label(word_count),
        })

    return render(
        request,
        "words/ready_sets.html",
        {
            "word_sets": ready_word_sets,
        }
    )


def study_set(request, slug):
    result = ""
    result_class = ""
    user_answer = ""
    show_next_button = False
    study_finished = False
    correct_answers = request.session.get("correct_answers", 0)
    wrong_answers = request.session.get("wrong_answers", 0)

    word_set = WordSet.objects.get(slug=slug)
    session_key = f"study_words_{word_set.id}"

    if session_key not in request.session:
        words = list(word_set.words.order_by("?"))
        request.session[session_key] = [word.id for word in words]

    if request.method == "POST":

        if "end_study" in request.POST:
            request.session.pop("correct_answers", None)
            request.session.pop("wrong_answers", None)
            request.session.pop(session_key, None)

            if word_set.is_public:
                return redirect("/ready-sets/")

            return redirect("/my-sets/")

        if "next_word" in request.POST:
            study_words = request.session.get(session_key, [])

            if study_words:
                word = Word.objects.get(id=study_words[0])
            else:
                word = None

            show_next_button = False

        elif "end_session" in request.POST:
            if "correct_answers" in request.session:
                del request.session["correct_answers"]
            if "wrong_answers" in request.session:
                del request.session["wrong_answers"]

            correct_answers, wrong_answers = 0, 0
            result = ""
            words = list(word_set.words.order_by("?"))
            request.session[session_key] = [word.id for word in words]

            study_words = request.session.get(session_key, [])

            if study_words:
                word = Word.objects.get(id=study_words[0])
            else:
                word = None
                study_finished = True

        else:
            word_id = request.POST.get("word_id")
            word = Word.objects.get(id=word_id)

            answer = request.POST.get("answer")
            user_answer = answer

            if word.text_en.strip().lower() == answer.strip().lower():
                result = "SUPER!"
                result_class = "success"
                correct_answers += 1
                request.session["correct_answers"] = correct_answers
                study_words = request.session.get(session_key, [])
                if study_words:
                    study_words.pop(0)
                    request.session[session_key] = study_words

                    if not study_words:
                        study_finished = True

            else:
                result = f"{word.text_en}"
                result_class = "danger"
                wrong_answers += 1
                request.session["wrong_answers"] = wrong_answers

                study_words = request.session.get(session_key, [])

                if study_words:
                    wrong_word_id = study_words.pop(0)

                    if len(study_words) > 1:
                        insert_index = random.randint(1, len(study_words))
                        study_words.insert(insert_index, wrong_word_id)
                    else:
                        study_words.append(wrong_word_id)

                    request.session[session_key] = study_words

            show_next_button = True

    else:
        if "correct_answers" in request.session:
            del request.session["correct_answers"]
        if "wrong_answers" in request.session:
            del request.session["wrong_answers"]

        correct_answers, wrong_answers = 0, 0

        study_words = request.session.get(session_key, [])

        if not study_words:
            words = list(word_set.words.order_by("?"))
            study_words = [word.id for word in words]
            request.session[session_key] = study_words

        if study_words:
            word = Word.objects.get(id=study_words[0])
        else:
            word = None
            study_finished = True

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
            "show_next_button": show_next_button,
            "user_answer": user_answer,
            "study_finished": study_finished,
        }
    )


@login_required
def my_sets(request):
    if request.method == "POST":
        delete_set_id = request.POST.get("delete_set_id")

        if delete_set_id:
            WordSet.objects.get(id=delete_set_id, is_public=False).delete()

        return redirect("/my-sets/")

    word_sets = WordSet.objects.filter(
        is_public=False,
        owner=request.user,)

    return render(
        request,
        "words/my_sets.html",
        {
            "word_sets": word_sets,
        }
    )


@login_required
def create_set(request):
    if request.method == "POST":
        name = request.POST.get("name")
        slug = slugify(name)

        word_set = WordSet.objects.create(
            name=name,
            slug=slug,
            owner=request.user
        )

        return redirect(f"/my-sets/{word_set.slug}/")

    return render(
        request,
        "words/create_set.html",
    )


@login_required
def my_set_detail(request, slug):
    word_set = WordSet.objects.get(
        slug=slug,
        owner=request.user,
        is_public=False,
    )
    message = ""

    if request.method == "POST":

        if "delete_words" in request.POST:
            selected_words = request.POST.getlist("selected_words")
            Word.objects.filter(id__in=selected_words, word_set=word_set).delete()

            return redirect(f"/my-sets/{word_set.slug}/")

        text_pl = request.POST.get("text_pl", "").strip()
        text_en = request.POST.get("text_en", "").strip()
        edit_word_id = request.POST.get("edit_word_id")

        if not text_pl or not text_en:
            message = "Uzupełnij oba pola przed dodaniem słówka"

            return render(
                request,
                "words/my_set_detail.html",
                {
                    "word_set": word_set,
                    "edit_word": None,
                    "message": message,
                }
            )

        if edit_word_id:
            duplicate_exists = Word.objects.filter(
                word_set=word_set,
                text_pl=text_pl,
                text_en=text_en
            ).exclude(id=edit_word_id).exists()
        else:
            duplicate_exists = Word.objects.filter(
                word_set=word_set,
                text_pl=text_pl,
                text_en=text_en
            ).exists()

        if duplicate_exists:
            message = "Takie słówko już istnieje w tym zestawie"

            return render(
                request,
                "words/my_set_detail.html",
                {
                    "word_set": word_set,
                    "edit_word": None,
                    "message": message,
                }
            )

        if edit_word_id:
            word = Word.objects.get(id=edit_word_id, word_set=word_set)
            word.text_pl = text_pl
            word.text_en = text_en
            word.save()

            return redirect(f"/my-sets/{word_set.slug}/")

        Word.objects.create(
            text_pl=text_pl,
            text_en=text_en,
            word_set=word_set,
            level=1
        )

        return redirect(f"/my-sets/{word_set.slug}/")

    edit_word_id = request.GET.get("edit_word")
    edit_word = None

    if edit_word_id:
        edit_word = Word.objects.get(id=edit_word_id, word_set=word_set)

    return render(
        request,
        "words/my_set_detail.html",
        {
            "word_set": word_set,
            "edit_word": edit_word,
            "message": message
        }
    )


def register(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)

        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("/")
    else:
        form = UserCreationForm()

    return render(
        request,
        "registration/register.html",
        {
            "form": form,
        }
    )
