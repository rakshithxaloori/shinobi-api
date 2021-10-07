from django.db import models
from rest_framework.serializers import ModelSerializer, SerializerMethodField

from league_of_legends.models import (
    LolProfile,
    Match,
    Participant,
    ParticipantStats,
    Team,
    VerifyLolProfile,
)
from league_of_legends.cache import get_champion_mini


class VerifyLolProfileSerializer(ModelSerializer):
    old_profile_icon = SerializerMethodField()
    new_profile_icon = SerializerMethodField()

    class Meta:
        model = VerifyLolProfile
        fields = ["summoner_name", "platform", "old_profile_icon", "new_profile_icon"]

    def get_old_profile_icon(self, obj):
        return "http://ddragon.leagueoflegends.com/cdn/11.19.1/img/profileicon/{}.png".format(
            obj.old_profile_icon
        )

    def get_new_profile_icon(self, obj):
        return "http://ddragon.leagueoflegends.com/cdn/11.19.1/img/profileicon/{}.png".format(
            obj.new_profile_icon
        )


###################################################


class LolProfileSerializer(ModelSerializer):
    username = SerializerMethodField()
    profile_icon = SerializerMethodField()

    class Meta:
        model = LolProfile
        fields = ["name", "profile_icon", "platform", "level", "username"]

    def get_username(self, obj):
        try:
            return obj.profile.user.username
        except Exception:
            return None

    def get_profile_icon(self, obj):
        return "http://ddragon.leagueoflegends.com/cdn/11.19.1/img/profileicon/{}.png".format(
            obj.profile_icon
        )


###################################################


class ParticipantStatsSerializer(ModelSerializer):
    items = SerializerMethodField()

    class Meta:
        model = ParticipantStats
        fields = ["assists", "deaths", "kills", "items"]

    def get_items(self, obj):
        return [
            {
                "key": item,
                "image": "https://ddragon.leagueoflegends.com/cdn/11.19.1/img/item/{}.png".format(
                    item
                ),
            }
            for item in obj.items
        ]


class ParticipantSerializer(ModelSerializer):
    # My Matches
    id = SerializerMethodField()
    creation = SerializerMethodField()
    champion = SerializerMethodField()
    stats = ParticipantStatsSerializer()
    team = SerializerMethodField()

    class Meta:
        model = Participant
        fields = [
            "id",
            "creation",
            "champion",
            "role",
            "stats",
            "team",
        ]
        read_only_fields = fields

    def get_id(self, obj):
        try:
            return obj.team.b_match.id
        except Exception:
            return obj.team.r_match.id

    def get_creation(self, obj):
        return obj.team.creation

    def get_champion(self, obj):
        return get_champion_mini(champion_key=obj.champion_key)

    def get_team(self, obj):
        return {"side": obj.team.color, "win": obj.team.win}


###################################################
class MatchParticipantSerializer(ModelSerializer):
    summoner = LolProfileSerializer()
    stats = ParticipantStatsSerializer()
    champion = SerializerMethodField()

    class Meta:
        model = Participant
        fields = ["summoner", "stats", "champion", "role"]

    def get_champion(self, obj):
        return get_champion_mini(champion_key=obj.champion_key)


class TeamSerializer(ModelSerializer):
    participants = SerializerMethodField()

    class Meta:
        model = Team
        fields = ["participants", "color", "win"]

    def get_participants(self, obj):
        return MatchParticipantSerializer(obj.participants, many=True).data


class MatchSerializer(ModelSerializer):
    blue_team = TeamSerializer()
    red_team = TeamSerializer()

    class Meta:
        model = Match
        fields = ["id", "creation", "blue_team", "red_team", "mode", "platform"]


# from league_of_legends.models import Match
# from league_of_legends.serializers import MatchSerializer
# match = Match.objects.first()
# serializer = MatchSerializer(match)
# serializer.data
