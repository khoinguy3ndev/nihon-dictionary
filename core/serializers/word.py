from rest_framework import serializers
from core.models import Word, WordMeaning, ExampleSentence, Favorite

class ExampleSentenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExampleSentence
        fields = ["id", "jp", "en", "source", "source_id"]

class WordMeaningSerializer(serializers.ModelSerializer):
    examples = ExampleSentenceSerializer(many=True, read_only=True)

    class Meta:
        model = WordMeaning
        fields = ["id", "meaning", "examples"]

class WordSerializer(serializers.ModelSerializer):
    meanings = WordMeaningSerializer(many=True, read_only=True)
    is_favorited = serializers.SerializerMethodField()

    class Meta:
        model = Word
        fields = [
            "id", "kanji", "kana", "parts_of_speech", "jlpt_level",
            "is_cached", "meanings", "is_favorited"
        ]

    def get_is_favorited(self, obj):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return Favorite.objects.filter(user=request.user, word=obj).exists()
        return False
