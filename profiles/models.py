from random import choice

from django.db import models

from authentication.models import User


def random_bio():
    bios = [
        "May the Force be with you.",
        "Carpe diem. Seize the day, boys. Make your lives extraordinary.",
        "My mama always said life was like a box of chocolates. You never know what you're gonna get.",
        "Hasta la vista, baby.",
        "I am Groot.",
        "This is Sparta!",
        "Wilsoooooooon!",
        "Why so serious?",
        "Is this your king?",
        "I live my life a quarter mile at a time.",
        "How you doin'?",
        "It's gonna be legen — wait for it — dary.",
    ]

    return choice(bios)


# Create your models here.
class Game(models.Model):
    id = models.CharField(max_length=10, primary_key=True)
    name = models.CharField(max_length=50, unique=True)
    game_code = models.CharField(max_length=5, unique=True)
    logo_url = models.URLField()

    def __str__(self):
        return "{} || {}".format(self.name, self.game_code)


class Profile(models.Model):
    # Stuff that you wanna show in user's profile
    user = models.OneToOneField(User, related_name="profile", on_delete=models.PROTECT)
    followings = models.ManyToManyField(
        User, related_name="follower", blank=True, through="Following"
    )
    bio = models.TextField(max_length=150, default=random_bio)
    follower_count = models.IntegerField(default=0)
    games = models.ManyToManyField(
        Game, related_name="played_by", blank=True, through="PlaysGame"
    )
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.user.username)

    class Meta:
        ordering = ["-created"]


class Following(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    profile = models.ForeignKey(Profile, on_delete=models.PROTECT)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return "{} follows {}".format(self.profile.user.username, self.user.username)


class PlaysGame(models.Model):
    game = models.ForeignKey(Game, on_delete=models.PROTECT)
    profile = models.ForeignKey(
        Profile, related_name="plays_game", on_delete=models.PROTECT
    )
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return "{} plays {}".format(self.profile.user.username, self.game.name)
