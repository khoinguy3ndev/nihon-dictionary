from rest_framework import serializers
from core.models import Favorite
from core.serializers.word import WordLiteSerializer

class FavoriteSerializer(serializers.ModelSerializer):
    word = WordLiteSerializer(read_only=True)
    class Meta:
        model = Favorite
        fields = ["id","word"]
