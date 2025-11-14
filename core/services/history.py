from core.models import SearchHistory

def save_search_history(user, words):
    """
    Lưu lịch sử tìm kiếm cho user.
    - Không lưu nếu user chưa login
    - Không lưu trùng 1 word cho cùng user
    """

    if not user or not user.is_authenticated:
        return
    
    # Lưu tối đa 1 từ (từ đầu tiên)
    for w in words[:1]:

        # ⭐ KIỂM TRA: nếu user đã từng search từ này thì bỏ qua
        exists = SearchHistory.objects.filter(user=user, word=w).exists()
        if exists:
            return   # không lưu nữa

        # ⭐ Nếu chưa tồn tại -> lưu mới
        SearchHistory.objects.create(user=user, word=w)
