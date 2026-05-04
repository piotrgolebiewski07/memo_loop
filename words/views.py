from django.http import HttpResponse
from words.models import Word


def index(request):
    words = Word.objects.order_by("?")[0]

    return HttpResponse(words.text_pl)

