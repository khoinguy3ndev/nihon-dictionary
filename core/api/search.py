from rest_framework import generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.db.models import Q, Prefetch

from core.models import Word, WordMeaning
from core.serializers.word import WordSerializer
from core.services.ingest import upsert_from_jisho


class SearchView(generics.ListAPIView):
    """Tìm kiếm từ vựng theo kanji hoặc kana"""
    serializer_class = WordSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        q = (self.request.query_params.get("q") or "").strip()
        if not q:
            return Word.objects.none()

        # load meanings + examples để tránh N+1
        base = Word.objects.all().prefetch_related(
            Prefetch(
                "meanings",
                queryset=WordMeaning.objects.all().prefetch_related("examples")
            )
        )

        # kiểm tra trong DB trước
        qs = base.filter(Q(kanji__icontains=q) | Q(kana__icontains=q))
        if qs.exists():
            return qs

        # nếu chưa có -> gọi Jisho API rồi upsert
        words = upsert_from_jisho(q)
        return base.filter(id__in=[w.id for w in words])

    def get_serializer_context(self):
        """Truyền request xuống serializer để kiểm tra is_favorited"""
        context = super().get_serializer_context()
        context["request"] = self.request
        return context


@api_view(["GET"])
@permission_classes([permissions.AllowAny])
def autocomplete(request):
    """API gợi ý từ (autocomplete)"""
    q = request.query_params.get("q", "")
    if not q:
        return Response([])

    qs = (
        Word.objects.filter(Q(kanji__icontains=q) | Q(kana__icontains=q))
        .values("id", "kanji", "kana")[:10]
    )
    return Response(list(qs))


class ReverseLookupView(generics.ListAPIView):
    """Tra ngược nghĩa tiếng Việt sang tiếng Nhật"""
    serializer_class = WordSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        q = (self.request.query_params.get("q") or "").strip()
        if not q:
            return Word.objects.none()

        # tìm trong DB trước
        ids = (
            Word.objects.filter(meanings__meaning__icontains=q)
            .values_list("id", flat=True)
            .distinct()
        )
        if ids:
            return Word.objects.filter(id__in=ids)

        # nếu chưa có -> gọi Jisho API rồi upsert
        words = upsert_from_jisho(q)
        return Word.objects.filter(id__in=[w.id for w in words])

    def get_serializer_context(self):
        """Truyền request xuống serializer để kiểm tra is_favorited"""
        context = super().get_serializer_context()
        context["request"] = self.request
        return context
