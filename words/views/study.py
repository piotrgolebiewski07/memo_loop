from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.urls import reverse

import random

from ..models import Word, WordSet, StudySession


def index(request):

    result = ""
    correct_answers = request.session.get("correct_answers", 0)
    wrong_answers = request.session.get("wrong_answers", 0)

    if request.method == "POST":

        if "end_session" in request.POST:

            request.session.pop("correct_answers", None)
            request.session.pop("wrong_answers", None)

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
        request.session.pop("correct_answers", None)
        request.session.pop("wrong_answers", None)

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


def study_set(request, slug):
    result = ""
    result_class = ""
    user_answer = ""
    show_next_button = False
    study_finished = False
    session_completed = False
    difficult_words_summary = []
    correct_answers = request.session.get("correct_answers", 0)
    wrong_answers = request.session.get("wrong_answers", 0)
    difficult_words = request.session.get("difficult_words", {})
    current_filter = request.GET.get("filter", "all")
    show_all = request.GET.get("show-all") == "true"

    if request.user.is_authenticated:
        word_set = get_object_or_404(
            WordSet,
            Q(slug=slug) &
            Q(is_deleted=False) &
            (Q(is_public=True) | Q(owner=request.user))
            )
    else:
        word_set = get_object_or_404(
            WordSet,
            slug=slug,
            is_deleted=False,
            is_public=True,
        )

    session_key = f"study_words_{word_set.id}"

    if session_key not in request.session:
        words = list(word_set.words.order_by("?"))
        request.session[session_key] = [word.id for word in words]

    if request.method == "POST":

        if "end_study" in request.POST:
            request.session.pop("correct_answers", None)
            request.session.pop("wrong_answers", None)
            request.session.pop("difficult_words", None)
            request.session.pop(session_key, None)

            if word_set.is_public and show_all:
                return redirect(f"{reverse('ready_sets')}?show-all=true")
            elif word_set.is_public:
                return redirect("ready_sets")

            return redirect(f"{reverse('my_sets')}?filter={current_filter}")

        if "next_word" in request.POST:
            study_words = request.session.get(session_key, [])

            if study_words:
                word = word_set.words.filter(id=study_words[0]).first()

                if word is None:
                    request.session.pop(session_key, None)
                    return redirect("study_set", slug=word_set.slug)
            else:
                word = None
                study_finished = True
                session_completed = True

            show_next_button = False

        elif "end_session" in request.POST:
            request.session.pop("correct_answers", None)
            request.session.pop("wrong_answers", None)

            request.session.pop("difficult_words", None)

            correct_answers, wrong_answers = 0, 0
            result = ""
            words = list(word_set.words.order_by("?"))
            request.session[session_key] = [word.id for word in words]

            study_words = request.session.get(session_key, [])

            if study_words:
                word = word_set.words.filter(id=study_words[0]).first()

                if word is None:
                    request.session.pop(session_key, None)
                    return redirect("study_set", slug=word_set.slug)
            else:
                word = None
                study_finished = True

        else:
            word_id = request.POST.get("word_id")
            word = word_set.words.filter(id=word_id).first()

            if word is None:
                request.session.pop(session_key, None)
                return redirect("study_set", slug=word_set.slug)

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

            else:
                result = f"{word.text_en}"
                result_class = "danger"
                wrong_answers += 1
                request.session["wrong_answers"] = wrong_answers

                study_words = request.session.get(session_key, [])

                word_id_str = str(word.id)
                difficult_words[word_id_str] = difficult_words.get(word_id_str, 0) + 1
                request.session["difficult_words"] = difficult_words

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
        request.session.pop("correct_answers", None)
        request.session.pop("wrong_answers", None)

        correct_answers, wrong_answers = 0, 0

        study_words = request.session.get(session_key, [])

        if not study_words:
            words = list(word_set.words.order_by("?"))
            study_words = [word.id for word in words]
            request.session[session_key] = study_words

        if study_words:
            word = word_set.words.filter(id=study_words[0]).first()

            if word is None:
                request.session.pop(session_key, None)
                return redirect("study_set", slug=word_set.slug)
        else:
            word = None
            study_finished = True

    total_answers = correct_answers + wrong_answers

    if total_answers > 0:
        success_rate = round((correct_answers / total_answers) * 100)
    else:
        success_rate = 0

    if session_completed and request.user.is_authenticated:
        StudySession.objects.create(
            user=request.user,
            word_set=word_set,
            correct_answers=correct_answers,
            wrong_answers=wrong_answers,
            success_rate=success_rate,
        )

    if study_finished:
        for word_id, mistakes in sorted(
                difficult_words.items(),
                key=lambda item: item[1],
                reverse=True,
        )[:2]:
            difficult_word = word_set.words.filter(id=int(word_id)).first()

            if difficult_word:
                difficult_words_summary.append({
                    "word": difficult_word,
                    "mistakes": mistakes,
                })

    if success_rate == 100:
        summary_title = "Idealnie!"
        summary_text = "Perfekcyjna sesja. Nie było ani jednego błędu."

    elif success_rate >= 70:
        summary_title = "Super!"
        summary_text = "Każda lekcja to krok do mistrzostwa."

    elif success_rate >= 50:
        summary_title = "Całkiem nieźle!"
        summary_text = "Widać postępy. Jeszcze trochę praktyki."

    elif success_rate >= 30:
        summary_title = "Jest postęp!"
        summary_text = "Nie zniechęcaj się. Każda powtórka pomaga."

    else:
        summary_title = "Nie poddawaj się!"
        summary_text = "Nawet najlepsi zaczynali od błędów."

    if success_rate >= 90:
        motivation_title = "Idealnie!"
        motivation_text = "Perfekcyjna sesja. Nie było ani jednego potknięcia."

    elif success_rate >= 75:
        motivation_title = "Świetna robota!"
        motivation_text = "Większość odpowiedzi była poprawna. Jesteś na dobrej drodze."

    elif success_rate >= 50:
        motivation_title = "Całkiem nieźle!"
        motivation_text = "Kilka błędów się pojawiło, ale właśnie tak wygląda nauka."

    elif success_rate >= 25:
        motivation_title = "Nie poddawaj się!"
        motivation_text = "Błędy pokazują, które słówka warto jeszcze powtórzyć."

    else:
        motivation_title = "Nie martw się błędami!"
        motivation_text = "To one sprawiają, że się uczysz i zapamiętujesz."

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
            "difficult_words_summary": difficult_words_summary,
            "summary_title": summary_title,
            "summary_text": summary_text,
            "motivation_title": motivation_title,
            "motivation_text": motivation_text,
        }
    )

