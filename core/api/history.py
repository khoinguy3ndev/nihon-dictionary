from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_search_history(request):
    """Trả về lịch sử tìm kiếm của user"""
    history = (
        request.user.searches
        .select_related("word")
        .order_by("-searched_at")[:30]
    )

    data = [
        {
            "id": h.word.id,
            "kanji": h.word.kanji,
            "kana": h.word.kana,
            "searched_at": h.searched_at
        }
        for h in history
    ]

    return Response(data)
