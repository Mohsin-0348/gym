from django.db import models


class UOMChoice(models.TextChoices):
    GRAM = 'gram'
    PIECE = 'piece'
    ML = 'ml'
    LITRE = 'litre'
    POUND = 'pound'
    CALORIE = 'calorie'


class MealTypeChoice(models.TextChoices):
    BREAKFAST = 'breakfast'
    LUNCH = 'lunch'
    DINNER = 'dinner'
    PRE_WORKOUT = 'pre-workout'
    POST_WORKOUT = 'post-workout'
