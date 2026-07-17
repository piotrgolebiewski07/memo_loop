from django.shortcuts import render
from django.db.models import Count

from ..models import WordSet
from ..services.labels import get_color, ready_sets_label, word_count_label


def home(request):
    return render(
        request,
        "words/home.html",
        )


def ready_sets(request):
    featured_word_sets = WordSet.objects.filter(is_public=True, is_deleted=False, is_featured=True)
    other_word_sets =  WordSet.objects.filter(is_public=True, is_deleted=False, is_featured=False)
    all_word_sets = WordSet.objects.filter(is_public=True, is_deleted=False)

    set_count = all_word_sets.count()
    ready_sets_count_label = ready_sets_label(set_count)
    ready_word_sets = []
    other_ready_word_sets = []

    for word_set in featured_word_sets:
        word_count = word_set.words.count()
        word_label = word_count_label(word_count)
        level_class = get_color(word_set.level)

        ready_word_sets.append({
            "set": word_set,
            "word_count": word_count,
            "word_label": word_label,
            "level_class": level_class,
            "image_path": f"images/{word_set.image}",
        })
    other_sets = request.GET.get("show-all")

    if other_sets:

        for word_set in other_word_sets:
            word_count = word_set.words.count()
            word_label = word_count_label(word_count)
            level_class = get_color(word_set.level)

            other_ready_word_sets.append({
                "set": word_set,
                "word_count": word_count,
                "word_label": word_label,
                "level_class": level_class,
                "image_path": f"images/{word_set.image}",
            })

    words_summary = all_word_sets.aggregate(total_words=Count("words"))
    total_words = words_summary["total_words"]
    total_words_label = word_count_label(total_words)

    return render(
        request,
        "words/ready_sets.html",
        {
            "word_sets": ready_word_sets,
            "other_word_sets": other_ready_word_sets,
            "set_count": set_count,
            "ready_sets_count_label": ready_sets_count_label,
            "total_words": total_words,
            "total_words_label": total_words_label,
            "other_sets": other_sets,
        }
    )

