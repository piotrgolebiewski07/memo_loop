from operator import itemgetter

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Max
from django.db.models.functions import Lower
from django.shortcuts import redirect, render, get_object_or_404
from django.utils.text import slugify
from django.urls import reverse

from ..models import StudySession, Word, WordSet
from ..services.labels import day_label, set_label
from ..statistics import get_completed_sessions, get_current_streak


@login_required
def my_sets(request):
    if request.method == "POST":
        delete_set_id = request.POST.get("delete_set_id")
        favorite_set_id = request.POST.get("favorite_set_id")
        next_url = request.POST.get("next", reverse("my_sets"))

        if favorite_set_id:
            word_set = get_object_or_404(
                WordSet,
                id=favorite_set_id,
                owner=request.user,
                is_public=False,
                is_deleted=False,
            )

            word_set.is_favorite = not word_set.is_favorite
            word_set.save()

        if delete_set_id:
            word_set = get_object_or_404(
                WordSet,
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

        return redirect("my_set_detail", slug=word_set.slug)

    return render(
        request,
        "words/create_set.html",
    )


@login_required
def my_set_detail(request, slug):
    word_set = get_object_or_404(
        WordSet,
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
                name_exists = WordSet.objects.filter(
                    name=new_name,
                    owner=request.user,
                    is_public=False,
                    is_deleted=False,
                ).exclude(id=word_set.id).exists()

                if name_exists:
                    message = "Zestaw o takiej nazwie już istnieje"

                    return render(
                        request,
                        "words/my_set_detail.html",
                        {
                            "word_set": word_set,
                            "edit_word": None,
                            "message": message,
                        }
                    )

                base_slug = slugify(new_name)
                new_slug = base_slug
                slug_number = 2

                while WordSet.objects.filter(slug=new_slug).exclude(id=word_set.id).exists():
                    new_slug = f"{base_slug}-{slug_number}"
                    slug_number += 1

                word_set.name = new_name
                word_set.slug = new_slug
                word_set.save()

            return redirect("my_set_detail", slug=word_set.slug)

        if "delete_words" in request.POST:
            selected_words = request.POST.getlist("selected_words")
            Word.objects.filter(id__in=selected_words, word_set=word_set).delete()

            return redirect("my_set_detail", slug=word_set.slug)

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
            word = get_object_or_404(Word, id=edit_word_id, word_set=word_set)
            word.text_pl = text_pl
            word.text_en = text_en
            word.save()

            return redirect("my_set_detail", slug=word_set.slug)

        Word.objects.create(
            text_pl=text_pl,
            text_en=text_en,
            word_set=word_set,
            level=1
        )

        return redirect("my_set_detail", slug=word_set.slug)

    edit_word_id = request.GET.get("edit_word")
    edit_word = None

    if edit_word_id:
        edit_word = get_object_or_404(Word, id=edit_word_id, word_set=word_set)

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
