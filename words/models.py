from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models


class Word(models.Model):
    text_pl = models.CharField(max_length=200)
    text_en = models.CharField(max_length=200)
    level = models.IntegerField(default=1,
                                validators=[MinValueValidator(1), MaxValueValidator(5)])
