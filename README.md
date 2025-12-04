# 日本語辞書 (Nihon Dictionary)

A Japanese-English dictionary API built with Django REST Framework. This backend service provides word search, kanji lookup, flashcard management, JLPT vocabulary practice, and translation features.

## Features

- **Word Search**: Search Japanese words by kanji or kana with results from [Jisho.org](https://jisho.org) API
- **Reverse Lookup**: Search Japanese words by English meaning
- **Autocomplete**: Get word suggestions as you type
- **Kanji Details**: Lookup detailed kanji information via [KanjiAPI](https://kanjiapi.dev)
- **Translation**: Translate Japanese text to English using Google Translate
- **JLPT Vocabulary**: Browse vocabulary lists by JLPT level (N5-N1)
- **Quiz Mode**: Generate JLPT vocabulary quizzes
- **User Authentication**: JWT-based authentication with user registration
- **Favorites**: Save favorite words for quick access
- **Flashcards**: Create and manage flashcard decks for vocabulary study
- **Search History**: Track your search history (authenticated users)
- **Example Sentences**: View example sentences from [Tatoeba](https://tatoeba.org)

## Tech Stack

- **Framework**: Django 5.2.5 with Django REST Framework
- **Database**: MySQL (utf8mb4 charset for Japanese character support)
- **Authentication**: JWT via `djangorestframework-simplejwt`
- **External APIs**:
  - [Jisho.org API](https://jisho.org/api/v1/search/words) - Japanese dictionary data
  - [KanjiAPI](https://kanjiapi.dev) - Kanji details
  - [Tatoeba](https://tatoeba.org) - Example sentences
  - Google Translate (via `deep-translator`) - Translation service
- **AI Integration**: Gemini API for enhanced features

## Prerequisites

- Python 3.10+
- MySQL 8.0+
- pip (Python package manager)

## Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/khoinguy3ndev/nihon-dictionary.git
   cd nihon-dictionary
   ```

2. **Create and activate a virtual environment**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**

   ```bash
   pip install django djangorestframework djangorestframework-simplejwt
   pip install mysqlclient python-dotenv requests deep-translator
   pip install django-cors-headers google-generativeai
   ```

   > **Tip**: Consider creating a `requirements.txt` file to track dependencies:
   > ```bash
   > pip freeze > requirements.txt
   > ```
   > Then install with: `pip install -r requirements.txt`

4. **Set up environment variables**

   Copy the example environment file and configure it:

   ```bash
   cp .env.example .env
   ```

   Edit `.env` and add your API key:

   ```
   GEMINI_API_KEY=your_gemini_api_key_here
   ```

5. **Configure the database**

   Create a MySQL database:

   ```sql
   CREATE DATABASE nihon_dict CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   ```

   Update database credentials in `backend/settings.py` if needed.

6. **Run migrations**

   ```bash
   python manage.py migrate
   ```

7. **Create a superuser (optional)**

   ```bash
   python manage.py createsuperuser
   ```

## Running the Server

Start the development server:

```bash
python manage.py runserver 8888
```

The API will be available at `http://localhost:8888/api/`

## API Endpoints

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register/` | Register a new user |
| POST | `/api/auth/token/` | Obtain JWT token |
| POST | `/api/auth/token/refresh/` | Refresh JWT token |
| GET | `/api/auth/me/` | Get current user info |
| PUT | `/api/auth/update/` | Update user profile |
| POST | `/api/auth/change-password/` | Change password |

### Search & Lookup

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/search/?q={query}` | Search words by kanji/kana |
| GET | `/api/reverse/?q={query}` | Reverse lookup by English meaning |
| GET | `/api/autocomplete/?q={query}` | Get autocomplete suggestions |
| GET | `/api/word/{id}/` | Get word details |
| GET | `/api/kanji/{char}/` | Get kanji details |

### Translation

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/translate/` | Translate Japanese text to English |

### JLPT & Quiz

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/jlpt/{level}/words/` | Get JLPT vocabulary list |
| POST | `/api/quiz/jlpt/` | Generate JLPT quiz |

### Favorites

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/favorites/` | List all favorites |
| POST | `/api/favorites/toggle/` | Toggle favorite status |
| GET | `/api/favorites/{word_id}/is_favorited/` | Check if word is favorited |

### Flashcards

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/flashcards/` | List all flashcard decks |
| POST | `/api/flashcards/create/` | Create a new flashcard deck |
| GET | `/api/flashcards/{id}/` | Get flashcard deck details |
| POST | `/api/flashcards/{id}/add/` | Add word to flashcard deck |
| GET | `/api/flashcards/{id}/is_in/` | Check if word is in deck |

### History

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/history/` | Get search history |

## Project Structure

```
nihon-dictionary/
├── backend/
│   ├── settings.py      # Django settings
│   ├── urls.py          # Root URL configuration
│   ├── wsgi.py          # WSGI configuration
│   └── asgi.py          # ASGI configuration
├── core/
│   ├── api/             # API views
│   │   ├── auth.py      # Authentication endpoints
│   │   ├── search.py    # Search endpoints
│   │   ├── favorites.py # Favorites endpoints
│   │   ├── flashcards.py # Flashcard endpoints
│   │   ├── translate.py # Translation endpoint
│   │   ├── kanji.py     # Kanji lookup
│   │   ├── jlpt.py      # JLPT vocabulary
│   │   ├── quiz.py      # Quiz generation
│   │   └── urls.py      # API URL routing
│   ├── models.py        # Database models
│   ├── serializers/     # DRF serializers
│   └── services/        # Business logic & external API clients
├── manage.py            # Django management script
├── .env.example         # Environment variables template
└── README.md            # This file
```

## Models

- **User**: Extended Django user with role support (user/admin)
- **Word**: Japanese vocabulary with kanji, kana, and JLPT level
- **WordMeaning**: Meanings for each word
- **ExampleSentence**: Example sentences from Tatoeba
- **SearchHistory**: User search history tracking
- **Favorite**: User's favorite words
- **Flashcard**: Flashcard deck with name
- **FlashcardWord**: Words in a flashcard deck

## License

This project is open source and available under the [MIT License](LICENSE).

## Acknowledgments

- [Jisho.org](https://jisho.org) for Japanese dictionary data
- [KanjiAPI](https://kanjiapi.dev) for kanji information
- [Tatoeba](https://tatoeba.org) for example sentences
- [Google Translate](https://translate.google.com) for translation services
