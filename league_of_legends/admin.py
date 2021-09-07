from django.contrib import admin

from league_of_legends.models import (
    LolProfile,
    Participant,
    ParticipantStats,
    Team,
    Match,
)

admin.site.register(LolProfile)
admin.site.register(Participant)
admin.site.register(ParticipantStats)
admin.site.register(Team)
admin.site.register(Match)
