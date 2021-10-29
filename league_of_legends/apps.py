from django.apps import AppConfig


class LeagueOfLegendsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "league_of_legends"

    def ready(self):
        import league_of_legends.signals
