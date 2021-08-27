from django.core.cache import cache

from rest_framework.serializers import ModelSerializer, SerializerMethodField

from league_of_legends.models import Participant, ParticipantStats
from league_of_legends.utils import get_champion_mini


class ParticipantStatsSerializer(ModelSerializer):
    items = SerializerMethodField()

    class Meta:
        model = ParticipantStats
        fields = ["assists", "deaths", "kills", "items"]

    def get_items(self, obj):
        return [
            "https://ddragon.leagueoflegends.com/cdn/11.16.1/img/item/{}.png".format(
                item
            )
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
