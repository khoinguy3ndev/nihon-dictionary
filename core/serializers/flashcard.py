from rest_framework import serializers
from core.models import Flashcard, FlashcardWord
from core.serializers.word import WordLiteSerializer

class FlashcardWordSerializer(serializers.ModelSerializer):
    word = WordLiteSerializer(read_only=True)
    class Meta:
        model = FlashcardWord
        fields = ["id","word"]

class FlashcardSerializer(serializers.ModelSerializer):
    items = FlashcardWordSerializer(many=True, read_only=True)
    class Meta:
        model = Flashcard
        fields = ["id","name","created_at","items"]
