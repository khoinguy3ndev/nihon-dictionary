from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    # giữ username/email như mặc định; thêm role
    ROLE_CHOICES = (('user','user'), ('admin','admin'))
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')

class Word(models.Model):
    kanji = models.CharField(max_length=255, null=True, blank=True)
    kana = models.CharField(max_length=255, null=True, blank=True)
    parts_of_speech = models.CharField(max_length=255)
    jlpt_level = models.CharField(max_length=10, null=True, blank=True)
    is_cached = models.BooleanField(default=False)

    def __str__(self): return self.kanji or self.kana or "word"

class WordMeaning(models.Model):
    word = models.ForeignKey(Word, on_delete=models.CASCADE, related_name='meanings')
    meaning = models.TextField()
    example_sentence = models.TextField(null=True, blank=True)

class SearchHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='searches')
    word = models.ForeignKey(Word, on_delete=models.CASCADE)
    searched_at = models.DateTimeField(auto_now_add=True)

class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
    word = models.ForeignKey(Word, on_delete=models.CASCADE)
    class Meta:
        unique_together = ('user','word')

class Flashcard(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='flashcards')
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

class FlashcardWord(models.Model):
    flashcard = models.ForeignKey(Flashcard, on_delete=models.CASCADE, related_name='items')
    word = models.ForeignKey(Word, on_delete=models.CASCADE)

# core/models.py
from django.db import models

class ExampleSentence(models.Model):
    meaning = models.ForeignKey(
        'core.WordMeaning', on_delete=models.CASCADE, related_name='examples'
    )
    jp = models.TextField()                         # câu JP
    en = models.TextField(null=True, blank=True)    # câu EN (nếu có)
    source = models.CharField(max_length=32, default='tatoeba')
    source_id = models.CharField(max_length=64, null=True, blank=True, db_index=True)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            # Nếu source_id có giá trị (Tatoeba có id), unique theo id là đủ.
            models.UniqueConstraint(
                fields=['meaning', 'source', 'source_id'],
                name='uq_example_by_sourceid'
            ),
        ]
