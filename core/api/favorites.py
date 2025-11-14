from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import generics

from core.models import Favorite, Word
from core.serializers.word import WordSerializer


# -----------------------------
# 1) Toggle favorite
# -----------------------------
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def toggle_favorite(request):
    word_id = request.data.get("word_id")
    if not word_id:
        return Response({"detail": "word_id required"}, status=400)

    fav, created = Favorite.objects.get_or_create(
        user=request.user, word_id=word_id
    )

    if not created:
        fav.delete()

    return Response({"favorited": created})


# -----------------------------
# 2) List all favorite WORDS (RETURN ARRAY, NO PAGINATION)
# -----------------------------
class FavoritesView(generics.ListAPIView):
    serializer_class = WordSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None  # ⭐ TẮT PAGINATION — QUAN TRỌNG

    def get_queryset(self):
        return Word.objects.filter(
            favorite__user=self.request.user
        ).distinct()


# -----------------------------
# 3) Check if 1 word is favorited
# -----------------------------
@api_view(["GET"])
@permission_classes([AllowAny])
def is_favorited(request, word_id):
    if not request.user.is_authenticated:
        return Response({"favorited": False})

    exists = Favorite.objects.filter(
        user=request.user, word_id=word_id
    ).exists()

    return Response({"favorited": exists})
