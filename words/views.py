from django.http import HttpResponse
from words.models import Word


def index(request):
    words = Word.objects.all()

    output = []

    for word in words:
        w = f"{word.text_pl} - {word.text_en}"
        output.append(w)
    return HttpResponse("<br>".join(output))

