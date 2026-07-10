from operator import itemgetter

from django.db.models.functions import Lower
from django.shortcuts import render, redirect
from django.utils.text import slugify
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.db.models import Avg, Max
from django.core.paginator import Paginator

from .models import WordSet, Word, StudySession

import random

from .statistics import get_current_streak, get_completed_sessions


def word_count_label(count):
    if count == 1:
        return "słówko"
    if count % 10 in [2, 3, 4] and count % 100 not in [12, 13, 14]:
        return "słówka"
    return "słówek"


def set_label(count):
    if count == 1:
        return "zestaw"

    if count % 100 in {12, 13, 14}:
        return "zestawów"

    if count % 10 in {2, 3, 4}:
        return "zestawy"

    return "zestawów"


def day_label(count):
    return "dzień" if count == 1 else "dni"


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
    word_sets = WordSet.objects.filter(is_public=True, is_deleted=False)

    ready_word_sets = []

    for word_set in word_sets:
        word_count = word_set.words.count()
        word_label = word_count_label(word_count)

        ready_word_sets.append({
            "set": word_set,
            "word_count": word_count,
            "word_label": word_label,
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
    session_completed = False
    difficult_words_sorted = []
    difficult_words_summary = []
    correct_answers = request.session.get("correct_answers", 0)
    wrong_answers = request.session.get("wrong_answers", 0)
    difficult_words = request.session.get("difficult_words", {})
    current_filter = request.GET.get("filter", "all")

    word_set = WordSet.objects.get(
        slug=slug,
        is_deleted=False
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

            if word_set.is_public:
                return redirect("/ready-sets/")

            return redirect(f"/my-sets/?filter={current_filter}")

        if "next_word" in request.POST:
            study_words = request.session.get(session_key, [])

            if study_words:
                word = word_set.words.filter(id=study_words[0]).first()

                if word is None:
                    request.session.pop(session_key, None)
                    return redirect(f"/study/{word_set.slug}/")
            else:
                word = None

            show_next_button = False

        elif "end_session" in request.POST:
            if "correct_answers" in request.session:
                del request.session["correct_answers"]
            if "wrong_answers" in request.session:
                del request.session["wrong_answers"]

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
                    return redirect(f"/study/{word_set.slug}/")
            else:
                word = None
                study_finished = True

        else:
            word_id = request.POST.get("word_id")
            word = word_set.words.filter(id=word_id).first()

            if word is None:
                request.session.pop(session_key, None)
                return redirect(f"/study/{word_set.slug}/")

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
                        session_completed = True

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
            word = word_set.words.filter(id=study_words[0]).first()

            if word is None:
                request.session.pop(session_key, None)
                return redirect(f"/study/{word_set.slug}/")
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
        difficult_words_sorted = sorted(
            difficult_words.items(),
            key=lambda item: item[1],
            reverse=True
        )

        difficult_words_summary = []

        for word_id, mistakes in difficult_words_sorted[:2]:
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


@login_required
def my_sets(request):
    if request.method == "POST":
        delete_set_id = request.POST.get("delete_set_id")
        favorite_set_id = request.POST.get("favorite_set_id")
        next_url = request.POST.get("next", "/my-sets/")

        if favorite_set_id:
            word_set = WordSet.objects.get(
                id=favorite_set_id,
                owner=request.user,
                is_public=False,
                is_deleted=False,
            )

            word_set.is_favorite = not word_set.is_favorite
            word_set.save()

        if delete_set_id:
            word_set = WordSet.objects.get(
                id=delete_set_id,
                is_public=False,
                owner=request.user,
                is_deleted=False,
            )

            word_set.is_deleted = True
            word_set.save()

        return redirect(next_url)

    current_filter = request.GET.get("filter", "all")
    search_query = request.GET.get("q", "").strip()
    sort_by = request.GET.get("sort", "newest")

    word_sets = WordSet.objects.filter(
        is_public=False,
        owner=request.user,
        is_deleted=False,
    )

    if current_filter == "favorites":
        word_sets = word_sets.filter(is_favorite=True)
    elif current_filter == "recent":
        word_sets = word_sets.annotate(last_used=Max("study_sessions__created_at")).order_by("-last_used")

    if search_query:
        word_sets = word_sets.filter(name__icontains=search_query)

    if sort_by == "name_asc":
        word_sets = word_sets.order_by(Lower("name"))
    elif sort_by == "name_desc":
        word_sets = word_sets.order_by(Lower("name").desc())

    if sort_by == "newest":
        word_sets = word_sets.order_by("-created_at")
    elif sort_by == "oldest":
        word_sets = word_sets.order_by("created_at")

    word_sets_data = []

    for word_set in word_sets:
        word_count = word_set.words.count()

        last_sessions = list(
            StudySession.objects.filter(
                user=request.user,
                word_set=word_set,
            ).order_by("-created_at")[:10]
        )

        if last_sessions:
            progress = round(sum(session.success_rate for session in last_sessions) / len(last_sessions)
                             )
        else:
            progress = 0

        word_sets_data.append({
            "set": word_set,
            "word_count": word_count,
            "progress": progress,
        })

    if sort_by == "word_count_asc":
        word_sets_data = sorted(word_sets_data, key=itemgetter("word_count"))
    elif sort_by == "word_count_desc":
        word_sets_data = sorted(word_sets_data, key=itemgetter("word_count"), reverse=True)

    if sort_by == "progress_asc":
        word_sets_data = sorted(word_sets_data, key=itemgetter("progress"))
    elif sort_by == "progress_desc":
        word_sets_data = sorted(word_sets_data, key=itemgetter("progress"), reverse=True)

    allowed_page_sizes = [5, 10, 20, 50]
    per_page = request.GET.get("per_page", 10)

    try:
        per_page = int(per_page)
    except ValueError:
        per_page = 10

    if per_page not in allowed_page_sizes:
        per_page = 10

    paginator = Paginator(word_sets_data, per_page)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    elided_page_range = paginator.get_elided_page_range(page_obj.number, on_each_side=1, on_ends=1)
    pagination_ellipsis = paginator.ELLIPSIS

    total_words = sum(item["word_count"] for item in word_sets_data)

    set_count = word_sets.count()
    pagination_set_label = "zestawu" if set_count == 1 else "zestawów"
    set_label_text = set_label(set_count)

    day_count = get_current_streak(request.user)
    day_label_text = day_label(day_count)

    number_of_sessions = get_completed_sessions(request.user)

    return render(
        request,
        "words/my_sets.html",
        {
            "word_sets": word_sets_data,
            "total_words": total_words,
            "set_count": set_count,
            "set_label": set_label_text,
            "day_count": day_count,
            "day_label": day_label_text,
            "number_of_sessions": number_of_sessions,
            "current_filter": current_filter,
            "page_obj": page_obj,
            "elided_page_range": elided_page_range,
            "pagination_ellipsis": pagination_ellipsis,
            "per_page": per_page,
            "allowed_page_sizes": allowed_page_sizes,
            "pagination_set_label": pagination_set_label,
            "search_query": search_query,
            "sort_by": sort_by,
        }
    )


@login_required
def create_set(request):
    if request.method == "POST":
        name = request.POST.get("name", "").strip()

        if not name:
            return render(
                request,
                "words/create_set.html",
                {
                    "message": "Podaj nazwę zestawu",
                    }
            )

        base_slug = slugify(name)
        actual_slug = base_slug
        slug_number = 2

        if WordSet.objects.filter(
            name=name,
            owner=request.user,
            is_public=False,
            is_deleted=False,
        ).exists():
            return render(
                request,
                "words/create_set.html",
                {
                    "message": "Zestaw o takiej nazwie już istnieje",
                }
            )

        while WordSet.objects.filter(slug=actual_slug).exists():
            actual_slug = f"{base_slug}-{slug_number}"
            slug_number += 1

        icon_data = request.POST.get("icon", "bi-journal-bookmark|stat-green")
        icon, icon_color = icon_data.split("|")

        word_set = WordSet.objects.create(
            name=name,
            slug=actual_slug,
            owner=request.user,
            icon=icon,
            icon_color=icon_color,
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
        is_deleted=False,
    )
    message = ""

    if request.method == "POST":

        if "update_set_name" in request.POST:
            new_name = request.POST.get("set_name", "").strip()

            if new_name:
                new_slug = slugify(new_name)

                slug_exists = WordSet.objects.filter(
                    slug=new_slug,
                    owner=request.user,
                    is_public=False,
                    is_deleted=False,
                ).exclude(id=word_set.id).exists()

                if slug_exists:
                    message = "Zestaw o takiej nazwie już itnieje"

                    return render(
                        request,
                        "words/my_set_detail.html",
                        {
                            "word_set": word_set,
                            "edit_word": None,
                            "message": message,
                        }
                    )

                word_set.name = new_name
                word_set.slug = new_slug
                word_set.save()

            return redirect(f"/my-sets/{word_set.slug}/")

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
            "message": message,
            "edit_set": request.GET.get("edit_set"),
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
