from rest_framework import generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.db.models import Q, Prefetch

from core.models import Word, WordMeaning
from core.serializers.word import WordSerializer
from core.services.ingest import upsert_from_jisho
from core.services.history import save_search_history


# ---------------------------------------------------------
#  SEARCH
# ---------------------------------------------------------
class SearchView(generics.ListAPIView):
    """
    Tìm kiếm từ vựng theo Kanji hoặc Kana.
    Nếu user đăng nhập -> lưu lịch sử tìm kiếm vào SearchHistory.
    """
    serializer_class = WordSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        request = self.request
        q = (request.query_params.get("q") or "").strip()

        if not q:
            return Word.objects.none()

        # Tránh N+1 queries: load meanings + examples
        base = Word.objects.all().prefetch_related(
            Prefetch(
                "meanings",
                queryset=WordMeaning.objects.all().prefetch_related("examples")
            )
        )

        # 1) Tìm trong DB trước
        qs = base.filter(Q(kanji__icontains=q) | Q(kana__icontains=q))

        if qs.exists():
            # ✔ LƯU LỊCH SỬ (nếu người dùng đăng nhập)
            save_search_history(request.user, list(qs))
            return qs

        # 2) Không có trong DB -> gọi Jisho API để lấy & lưu
        words = upsert_from_jisho(q)
        result = base.filter(id__in=[w.id for w in words])

        # ✔ LƯU LỊCH SỬ
        save_search_history(request.user, list(result))
        return result

    def get_serializer_context(self):
        """
        Truyền request xuống serializer để xử lý is_favorited.
        """
        context = super().get_serializer_context()
        context["request"] = self.request
        return context


# ---------------------------------------------------------
#  AUTOCOMPLETE
# ---------------------------------------------------------
@api_view(["GET"])
@permission_classes([permissions.AllowAny])
def autocomplete(request):
    """API gợi ý từ (autocomplete)"""
    q = request.query_params.get("q", "").strip()
    if not q:
        return Response([])

    qs = (
        Word.objects.filter(Q(kanji__icontains=q) | Q(kana__icontains=q))
        .values("id", "kanji", "kana")[:10]
    )
    return Response(list(qs))


# ---------------------------------------------------------
#  REVERSE LOOKUP (Tra nghĩa tiếng Việt -> tiếng Nhật)
# ---------------------------------------------------------
class ReverseLookupView(generics.ListAPIView):
    """
    Tra ngược nghĩa tiếng Việt sang tiếng Nhật.
    Nếu user đăng nhập -> lưu lịch sử tìm kiếm.
    """
    serializer_class = WordSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        request = self.request
        q = (request.query_params.get("q") or "").strip()
        if not q:
            return Word.objects.none()

        # 1) Tìm trong DB trước
        ids = (
            Word.objects.filter(meanings__meaning__icontains=q)
            .values_list("id", flat=True)
            .distinct()
        )

        if ids:
            qs = Word.objects.filter(id__in=ids)
            # ✔ LƯU LỊCH SỬ
            save_search_history(request.user, list(qs))
            return qs

        # 2) Không có -> gọi Jisho API
        words = upsert_from_jisho(q)
        result = Word.objects.filter(id__in=[w.id for w in words])

        # ✔ LƯU LỊCH SỬ
        save_search_history(request.user, list(result))
        return result

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context
