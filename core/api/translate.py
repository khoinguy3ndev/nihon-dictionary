from deep_translator import GoogleTranslator
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

@api_view(["POST"])
@permission_classes([AllowAny])
def translate_text(request):
    text = request.data.get("text", "").strip()
    if not text:
        return Response({"error": "Empty text"}, status=400)

    try:
        translated = GoogleTranslator(source="ja", target="en").translate(text)
        return Response({"translated": translated})
    except Exception as e:
        return Response({"error": str(e)}, status=500)
