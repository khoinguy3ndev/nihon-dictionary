from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import generics
from core.models import Flashcard, FlashcardWord
from core.serializers.flashcard import FlashcardSerializer

@api_view(["POST"])
def create_flashcard(request):
    if not request.user.is_authenticated:
        return Response(status=401)
    name = request.data.get("name", "My deck")
    fc = Flashcard.objects.create(user=request.user, name=name)
    return Response({"id": fc.id, "name": fc.name}, status=201)

@api_view(["POST"])
def add_to_flashcard(request, flashcard_id):
    if not request.user.is_authenticated:
        return Response(status=401)
    word_id = request.data.get("word_id")
    if not word_id:
        return Response({"detail": "word_id required"}, status=400)
    FlashcardWord.objects.get_or_create(flashcard_id=flashcard_id, word_id=word_id)
    return Response({"ok": True})

class FlashcardDetail(generics.RetrieveAPIView):
    queryset = Flashcard.objects.all()
    serializer_class = FlashcardSerializer
