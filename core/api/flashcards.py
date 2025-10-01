from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import generics, status
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated


from core.models import Flashcard, FlashcardWord
from core.serializers.flashcard import FlashcardSerializer


@api_view(["POST"])
def create_flashcard(request):
    if not request.user.is_authenticated:
        return Response(status=401)

    name = request.data.get("name", "My deck")

    # Nếu đã có flashcard với tên này thì dùng lại, không tạo mới
    fc, created = Flashcard.objects.get_or_create(
        user=request.user,
        name=name
    )

    return Response({"id": fc.id, "name": fc.name}, status=201 if created else 200)


@api_view(["POST"])
def add_to_flashcard(request, flashcard_id):
    if not request.user.is_authenticated:
        return Response(status=401)

    word_id = request.data.get("word_id")
    if not word_id:
        return Response({"detail": "word_id required"}, status=400)

    # 🔎 Tìm flashcard thuộc về user hiện tại
    try:
        flashcard = Flashcard.objects.get(id=flashcard_id, user=request.user)
    except Flashcard.DoesNotExist:
        return Response({"detail": "Flashcard not found"}, status=404)

    # Thêm từ vào flashcard
    FlashcardWord.objects.get_or_create(
        flashcard=flashcard,
        word_id=word_id
    )

    return Response({"ok": True})


class FlashcardDetail(generics.RetrieveAPIView):
    """Xem chi tiết flashcard (chỉ nếu thuộc về user hiện tại)"""
    serializer_class = FlashcardSerializer

    def get_queryset(self):
        return Flashcard.objects.filter(user=self.request.user)


@api_view(["GET"])
def list_flashcards(request):
    """Danh sách flashcards của user đang đăng nhập"""
    if not request.user.is_authenticated:
        return Response({"detail": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)

    flashcards = Flashcard.objects.filter(user=request.user).order_by("-created_at")
    data = FlashcardSerializer(flashcards, many=True).data
    return Response(data)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def is_in_flashcard(request, flashcard_id):
    """
    Kiểm tra 1 từ đã nằm trong flashcard của user chưa
    GET /api/flashcards/<flashcard_id>/is_in/?word_id=123
    """
    word_id = request.query_params.get("word_id")
    if not word_id:
        return Response({"detail": "Thiếu word_id"}, status=400)

    try:
        flashcard = Flashcard.objects.get(id=flashcard_id, user=request.user)
    except Flashcard.DoesNotExist:
        return Response({"detail": "Không tìm thấy flashcard"}, status=404)

    exists = FlashcardWord.objects.filter(
        flashcard=flashcard, word_id=word_id
    ).exists()

    return Response({"in_flashcard": exists})