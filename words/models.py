from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.contrib.auth.models import User


class WordSet(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=100)
    level = models.CharField(max_length=10)
    slug = models.SlugField(unique=True)
    is_public = models.BooleanField(default=False)
    is_favorite = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    icon = models.CharField(max_length=50, default="bi-journal-bookmark")
    icon_color = models.CharField(max_length=30, default="stat-green")
    created_at = models.DateTimeField(auto_now_add=True)
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


class StudySession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="study_sessions")
    word_set = models.ForeignKey(WordSet, on_delete=models.CASCADE, related_name="study_sessions")

    correct_answers = models.PositiveIntegerField(default=0)
    wrong_answers = models.PositiveIntegerField(default=0)
    success_rate = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.word_set.name} - {self.success_rate}%"




