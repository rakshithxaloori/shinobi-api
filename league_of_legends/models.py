from django.db import models

from profiles.models import Profile

# Create your models here.
class LolProfile(models.Model):
    # Max lengths are noted from the link below
    # https://developer.riotgames.com/apis#summoner-v4/GET_getByPUUID

    # TODO check if Riot OAuth returns accounts from all regions
    # That way you'd know if the accounts are preserved or deleted
    # when players switch regions and their summoner_id changes

    puuid = models.CharField(max_length=78, primary_key=True)
    # profile is
    # null or blank when summoner hasn't signed up for proeliumx yet
    # but has participant data
    profile = models.OneToOneField(
        Profile,
        related_name="lol_profile",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )
    name = models.CharField(max_length=16, null=False, blank=False)
    profile_icon = models.PositiveSmallIntegerField(default=0)
    level = models.PositiveSmallIntegerField(default=0)
    summoner_id = models.CharField(max_length=63)
    active = models.BooleanField(default=False)
    updating = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Team(models.Model):
    class Color(models.TextChoices):
        blue = "B"
        red = "R"

    # creation is same as Match.creation
    creation = models.DateTimeField(blank=False, null=False)
    color = models.CharField(
        max_length=1, choices=Color.choices, blank=False, null=False
    )  # color.label
    win = models.BooleanField(blank=False, null=False)

    def __str__(self):
        win_str = "WIN" if self.win else "LOSE"
        return "{} || {} || {}".format(self.creation, self.color, win_str)


class ParticipantStats(models.Model):
    assists = models.PositiveSmallIntegerField(null=False, blank=False)
    deaths = models.PositiveSmallIntegerField(null=False, blank=False)
    kills = models.PositiveSmallIntegerField(null=False, blank=False)
    # items is JSON string of [{"name", "image"}]
    # eg [{"name": "Sorcerer's Shoes", "image": "3020.png'"}, ...]
    items = models.JSONField(null=False, blank=False)

    def __str__(self):
        try:
            return "{} || {}/{}/{}".format(
                self.participant.summoner.name, self.assists, self.deaths, self.kills
            )
        except Exception:
            # Happens in admin panel
            # after deleting a participant
            # then trying to delete participantstats
            return "<participant> DELETED"


class Participant(models.Model):
    # If lolprofile doesn't exist, create but don't attach it a profile yet
    summoner = models.ForeignKey(
        LolProfile, related_name="participations", on_delete=models.PROTECT
    )
    team = models.ForeignKey(
        Team, related_name="participants", on_delete=models.PROTECT
    )
    stats = models.OneToOneField(
        ParticipantStats, related_name="participant", on_delete=models.PROTECT
    )
    # https://ddragon.leagueoflegends.com/cdn/11.17.1/img/champion/{}.png
    champion_key = models.PositiveSmallIntegerField(null=False, blank=False)
    role = models.CharField(max_length=15, null=False, blank=False)

    def __str__(self):
        return "{} || {} || {}".format(
            self.summoner.name, self.team.color, self.champion_key
        )


class Match(models.Model):
    id = models.CharField(primary_key=True, max_length=15)
    creation = models.DateTimeField(blank=False, null=False)
    blue_team = models.OneToOneField(
        Team, related_name="b_match", on_delete=models.PROTECT
    )
    red_team = models.OneToOneField(
        Team, related_name="r_match", on_delete=models.PROTECT
    )
    mode = models.CharField(max_length=30, blank=False, null=False)
    region = models.CharField(max_length=5, blank=False, null=False)

    def __str__(self):
        return "{} || {}".format(self.creation, self.id)
