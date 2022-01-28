from rest_framework.serializers import ModelSerializer


from settings.models import PrivacySettings


class PrivacySettingsSerializer(ModelSerializer):
    class Meta:
        model = PrivacySettings
        fields = ["show_flag"]
