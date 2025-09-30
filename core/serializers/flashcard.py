from rest_framework import serializers
from core.models import Flashcard, FlashcardWord
from .word import WordSerializer

class FlashcardWordSerializer(serializers.ModelSerializer):
    word = WordSerializer(read_only=True)

    class Meta:
        model = FlashcardWord
        fields = ["id", "word"]

class FlashcardSerializer(serializers.ModelSerializer):
    items = FlashcardWordSerializer(many=True, read_only=True)

    class Meta:
        model = Flashcard
        fields = ["id", "name", "created_at", "items"]
