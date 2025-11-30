import time
import logging
from rest_framework import generics, permissions
from rest_framework.response import Response
from core.models import Word
from core.serializers.word import WordSerializer
from core.services.ingest import _fill_examples_for_word

logger = logging.getLogger(__name__)


class WordDetailView(generics.RetrieveAPIView):
    queryset = Word.objects.all()
    serializer_class = WordSerializer
    permission_classes = [permissions.AllowAny]

    def get(self, request, *args, **kwargs):
        word = self.get_object()

        # Kiểm tra meaning đã có example chưa
        need_fetch = False
        for m in word.meanings.all():
            if m.examples.count() == 0:
                need_fetch = True
                break

        if need_fetch:
            start = time.perf_counter()
            _fill_examples_for_word(word, per_meaning=3)
            logger.info(f"[TIMING] DetailView fetch examples: {(time.perf_counter() - start) * 1000:.2f}ms")

        # Serialize lại (sau khi example đã được thêm)
        serializer = self.get_serializer(word)
        return Response(serializer.data)
