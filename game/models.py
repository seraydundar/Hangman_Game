from django.db import models
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.models import User

class Word(models.Model):
    text = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.text


class Points(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    score = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.user.username}: {self.score}"

class Hint(models.Model):
    # Her Word kaydı için bir ipucu saklayacak şekilde OneToOneField kullanıyoruz.
    word = models.OneToOneField(Word, on_delete=models.CASCADE, related_name="hint")
    hint_text = models.CharField(max_length=255, help_text="Kelimeye ait ipucu")

    def __str__(self):
        return f"Ipucu: {self.hint_text} ({self.word.text})"