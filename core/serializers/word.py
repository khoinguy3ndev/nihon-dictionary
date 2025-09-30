from rest_framework import serializers
from core.models import Word, WordMeaning, ExampleSentence

class ExampleSentenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExampleSentence
        fields = ["id", "jp", "en", "source", "source_id"]

class WordMeaningSerializer(serializers.ModelSerializer):
    examples = ExampleSentenceSerializer(many=True, read_only=True)
    class Meta:
        model = WordMeaning
        fields = ["id","meaning", "examples"]

class WordSerializer(serializers.ModelSerializer):
    meanings = WordMeaningSerializer(many=True, read_only=True)
    class Meta:
        model = Word
        fields = ["id","kanji","kana","parts_of_speech","jlpt_level","is_cached","meanings"]