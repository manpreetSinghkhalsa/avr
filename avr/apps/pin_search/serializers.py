from rest_framework import serializers

from apps.pin_search.models import OfficeLocation


class SearchSerializer(serializers.Serializer):
    """
    Sentiment Serializer
    """
    pincode = serializers.CharField()
    state = serializers.CharField()
    division_name = serializers.CharField()
    region_name = serializers.CharField()
    circle_name = serializers.CharField()
    taluk = serializers.CharField()
