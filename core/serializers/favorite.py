from rest_framework import serializers
from core.models import Favorite
from .word import WordSerializer

class FavoriteSerializer(serializers.ModelSerializer):
    word = WordSerializer(read_only=True)

    class Meta:
        model = Favorite
        fields = ["id", "word"]