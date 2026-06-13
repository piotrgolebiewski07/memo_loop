from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.contrib.auth.models import User


class WordSet(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    is_public = models.BooleanField(default=False)
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="word_sets",
        null=True,
        blank=True
    )

    def __str__(self):
        return self.name


class Word(models.Model):
    text_pl = models.CharField(max_length=200)
    text_en = models.CharField(max_length=200)
    level = models.IntegerField(default=1,
                                validators=[MinValueValidator(1), MaxValueValidator(5)])
    word_set = models.ForeignKey(
        WordSet,
        on_delete=models.CASCADE,
        related_name="words",
        null=True,
        blank=True
    )

    def __str__(self):
        return f"{self.text_pl} - {self.text_en}"

