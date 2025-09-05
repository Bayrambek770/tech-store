from rest_framework import serializers

from payment.utils import PaylovMethods


class PaylovSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    method = serializers.ChoiceField(choices=PaylovMethods.choices())
    params = serializers.JSONField()
