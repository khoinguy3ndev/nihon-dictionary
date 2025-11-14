from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from core.services.quiz import generate_jlpt_quiz


@api_view(["POST"])
@permission_classes([AllowAny])
def jlpt_quiz(request):
    level = request.data.get("level", "N5")
    count = int(request.data.get("count", 10))

    try:
        questions = generate_jlpt_quiz(level, count)
        return Response({
            "level": level,
            "count": len(questions),
            "questions": questions
        })

    except Exception as e:
        return Response({"detail": str(e)}, status=500)
