from rest_framework.serializers import ModelSerializer


from ux.models import AppUpdate

##########################################
class AppUpdateSerializer(ModelSerializer):
    class Meta:
        model = AppUpdate
        fields = ["version", "updates"]
        read_only_fields = fields
