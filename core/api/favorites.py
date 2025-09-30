from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import generics
from core.models import Favorite
from core.serializers.favorite import FavoriteSerializer

@api_view(["POST"])
def toggle_favorite(request):
    if not request.user.is_authenticated:
        return Response(status=401)
    word_id = request.data.get("word_id")
    if not word_id:
        return Response({"detail": "word_id required"}, status=400)
    fav, created = Favorite.objects.get_or_create(user=request.user, word_id=word_id)
    if not created:
        fav.delete()
    return Response({"favorited": created})

class FavoritesView(generics.ListAPIView):
    serializer_class = FavoriteSerializer
    def get_queryset(self):
        return Favorite.objects.filter(user=self.request.user)
