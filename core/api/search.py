import time
import logging

from rest_framework import generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.db.models import Q, Prefetch

from core.models import Word, WordMeaning
from core.serializers.word import WordSerializer
from core.services.ingest import upsert_from_jisho
from core.services.history import save_search_history

logger = logging.getLogger(__name__)


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
        total_start = time.perf_counter()
        request = self.request
        q = (request.query_params.get("q") or "").strip()

        if not q:
            return Word.objects.none()

        # Tránh N+1 queries: load meanings + examples
        t0 = time.perf_counter()
        base = Word.objects.all().prefetch_related(
            Prefetch(
                "meanings",
                queryset=WordMeaning.objects.all().prefetch_related("examples")
            )
        )
        logger.info(f"[TIMING] SearchView - build base queryset: {(time.perf_counter() - t0) * 1000:.2f}ms")

        # 1) Tìm trong DB trước
        t1 = time.perf_counter()
        qs = base.filter(Q(kanji__icontains=q) | Q(kana__icontains=q))
        exists = qs.exists()
        logger.info(f"[TIMING] SearchView - DB filter + exists check: {(time.perf_counter() - t1) * 1000:.2f}ms, found={exists}")

        if exists:
            # ✔ LƯU LỊCH SỬ (nếu người dùng đăng nhập)
            t2 = time.perf_counter()
            save_search_history(request.user, list(qs))
            logger.info(f"[TIMING] SearchView - save_search_history: {(time.perf_counter() - t2) * 1000:.2f}ms")
            logger.info(f"[TIMING] SearchView TOTAL (cache hit): {(time.perf_counter() - total_start) * 1000:.2f}ms")
            return qs

        # 2) Không có trong DB -> gọi Jisho API để lấy & lưu
        t3 = time.perf_counter()
        words = upsert_from_jisho(q)
        logger.info(f"[TIMING] SearchView - upsert_from_jisho: {(time.perf_counter() - t3) * 1000:.2f}ms")

        t4 = time.perf_counter()
        result = base.filter(id__in=[w.id for w in words])
        logger.info(f"[TIMING] SearchView - filter result: {(time.perf_counter() - t4) * 1000:.2f}ms")

        # ✔ LƯU LỊCH SỬ
        t5 = time.perf_counter()
        save_search_history(request.user, list(result))
        logger.info(f"[TIMING] SearchView - save_search_history: {(time.perf_counter() - t5) * 1000:.2f}ms")
        logger.info(f"[TIMING] SearchView TOTAL (cache miss): {(time.perf_counter() - total_start) * 1000:.2f}ms")
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
