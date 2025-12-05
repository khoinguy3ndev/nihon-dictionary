# 🇯🇵 Nihon Dictionary - Backend API

<div align="center">

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Django](https://img.shields.io/badge/Django-5.2-092E20?style=for-the-badge&logo=django&logoColor=white)
![DRF](https://img.shields.io/badge/Django_REST_Framework-3.14+-ff1709?style=for-the-badge&logo=django&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)


**A comprehensive Japanese-English dictionary REST API with AI-powered features**

[Features](#-features) • [Tech Stack](#-tech-stack) • [Installation](#-installation) • [API Documentation](#-api-documentation) • [Architecture](#-architecture)

</div>

---

## 📋 Overview

**Nihon Dictionary** is a full-featured Japanese dictionary backend service that provides:
- Japanese word search with Kanji/Kana support
- AI-powered JLPT quiz generation
- Flashcard management for vocabulary learning
- User authentication with JWT tokens

This project demonstrates proficiency in building scalable RESTful APIs, integrating multiple external services, and implementing modern authentication patterns.

---

## ✨ Features

### 🔍 **Dictionary & Search**
| Feature | Description |
|---------|-------------|
| **Word Search** | Search Japanese words by Kanji or Kana with auto-caching |
| **Reverse Lookup** | Find Japanese words by English meaning |
| **Autocomplete** | Real-time search suggestions |
| **Kanji Details** | Detailed Kanji information (readings, meanings, JLPT level, grade) |
| **Example Sentences** | Japanese-English example sentences from Tatoeba |

### 🎯 **Learning Tools**
| Feature | Description |
|---------|-------------|
| **JLPT Word Lists** | Browse vocabulary by JLPT level (N5-N1) |
| **AI Quiz Generator** | Generate JLPT-style grammar quizzes using Google Gemini AI |
| **Flashcards** | Create and manage custom flashcard decks |
| **Favorites** | Save words for quick access |
| **Search History** | Track and review searched words |

### 🔐 **Authentication & Security**
| Feature | Description |
|---------|-------------|
| **JWT Authentication** | Secure token-based authentication |
| **User Registration** | Email-required registration with validation |
| **Password Reset** | Email-based password recovery flow |
| **Role-based Access** | User/Admin role differentiation |

### 🌐 **Translation**
| Feature | Description |
|---------|-------------|
| **Japanese → English** | Real-time translation using Google Translate |

---

## 🛠 Tech Stack

### **Core Framework**
- **Python 3.10+** - Programming language
- **Django 5.2** - Web framework
- **Django REST Framework** - RESTful API toolkit
- **Simple JWT** - JSON Web Token authentication

### **Database**
- **PostgreSQL**

### **External APIs & Services**
| Service | Purpose |
|---------|---------|
| [Jisho API](https://jisho.org/) | Japanese dictionary data source |
| [Tatoeba API](https://tatoeba.org/) | Example sentences corpus |
| [KanjiAPI](https://kanjiapi.dev/) | Kanji character details |
| [Google Gemini AI](https://ai.google.dev/) | JLPT quiz generation |
| [Google Translate](https://translate.google.com/) | Translation service |

### **Additional Libraries**
- `python-dotenv` - Environment variable management
- `django-cors-headers` - CORS handling
- `requests` - HTTP client for external APIs
- `deep-translator` - Translation wrapper
- `google-generativeai` - Gemini AI SDK

---

## 📦 Installation

### Prerequisites
- Python 3.10 or higher
- PostgreSQL
- pip (Python package manager)

### Step 1: Clone the Repository
```bash
git clone https://github.com/khoinguyen2010hihihi/nihon-dictionary.git
cd nihon-dictionary/backend
```

### Step 2: Create Virtual Environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install django djangorestframework djangorestframework-simplejwt
pip install psycopg2-binary python-dotenv django-cors-headers
pip install requests deep-translator google-generativeai
```

### Step 4: Configure Environment Variables
```bash
# Copy example env file
cp .env.example .env

# Edit .env with your configurations
```

**.env configuration:**
```dotenv
# AI Service
GEMINI_API_KEY=your_gemini_api_key_here

# Email (for password reset)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASS=your_app_password

# Frontend URL (for password reset links)
FRONTEND_URL=http://localhost:3000
```

### Step 5: Configure Database
Update `backend/settings.py` with your PostgreSQL credentials:
```python
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("DB_NAME"),
        "USER": os.getenv("DB_USER", "postgres"),
        "PASSWORD": os.getenv("DB_PASSWORD"),
        "HOST": os.getenv("DB_HOST"),
        "PORT": os.getenv("DB_PORT"),
    }
}
```

### Step 6: Run Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### Step 7: Start Development Server
```bash
python manage.py runserver
```

The API will be available at `http://127.0.0.1:8000/api/`

---

## 📚 API Documentation

### Base URL
```
http://localhost:8000/api/
```

### Authentication
All protected endpoints require JWT token in header:
```
Authorization: Bearer <access_token>
```

---

### 🔐 Authentication Endpoints

#### Register
```http
POST /api/auth/register/
Content-Type: application/json

{
    "username": "johndoe",
    "email": "john@example.com",
    "password": "securepassword123"
}
```

**Response (201):**
```json
{
    "user": {
        "id": 1,
        "username": "johndoe",
        "email": "john@example.com",
        "role": "user",
        "date_joined": "2025-12-04T10:00:00Z"
    },
    "access": "eyJ0eXAiOiJKV1QiLCJhbGci...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGci..."
}
```

#### Get Current User
```http
GET /api/auth/me/
Authorization: Bearer <token>
```

#### Forgot Password
```http
POST /api/auth/forgot-password/
Content-Type: application/json

{
    "email": "john@example.com"
}
```

#### Reset Password
```http
POST /api/auth/reset-password/
Content-Type: application/json

{
    "token": "reset_token_from_email",
    "new_password": "newsecurepassword123"
}
```

---

### 🔍 Search Endpoints

#### Search Words
```http
GET /api/search/?q=日本語
```

**Response:**
```json
{
    "count": 5,
    "results": [
        {
            "id": 1,
            "kanji": "日本語",
            "kana": "にほんご",
            "parts_of_speech": "Noun",
            "jlpt_level": "N5",
            "meanings": [
                {
                    "id": 1,
                    "meaning": "Japanese language",
                    "examples": [
                        {
                            "jp": "日本語を勉強しています。",
                            "en": "I am studying Japanese."
                        }
                    ]
                }
            ]
        }
    ]
}
```

#### Autocomplete
```http
GET /api/autocomplete/?q=にほ
```

#### Reverse Lookup (English → Japanese)
```http
GET /api/reverse/?q=beautiful
```

#### Get Word Detail
```http
GET /api/word/{id}/
```

---

### 📖 Kanji Endpoints

#### Get Kanji Details
```http
GET /api/kanji/日/
```

**Response:**
```json
{
    "kanji": "日",
    "meanings": ["day", "sun", "Japan"],
    "on_readings": ["ニチ", "ジツ"],
    "kun_readings": ["ひ", "か"],
    "jlpt": 5,
    "grade": 1
}
```

---

### 🎯 JLPT Endpoints

#### Get JLPT Word List
```http
GET /api/jlpt/N5/words/
```

#### Generate JLPT Quiz (AI-Powered)
```http
POST /api/quiz/jlpt/
Content-Type: application/json

{
    "level": "N5",
    "count": 10
}
```

**Response:**
```json
{
    "questions": [
        {
            "sentence": "明日＿＿＿学校に行きます。",
            "choices": ["は", "が", "を", "に"],
            "correct_index": 0
        }
    ]
}
```

---

### ⭐ Favorites Endpoints

#### Toggle Favorite
```http
POST /api/favorites/toggle/
Authorization: Bearer <token>
Content-Type: application/json

{
    "word_id": 1
}
```

#### Get User's Favorites
```http
GET /api/favorites/
Authorization: Bearer <token>
```

#### Check if Favorited
```http
GET /api/favorites/{word_id}/is_favorited/
Authorization: Bearer <token>
```

---

### 📝 Flashcard Endpoints

#### List Flashcards
```http
GET /api/flashcards/
Authorization: Bearer <token>
```

#### Create Flashcard
```http
POST /api/flashcards/create/
Authorization: Bearer <token>
Content-Type: application/json

{
    "name": "JLPT N5 Vocabulary"
}
```

#### Add Word to Flashcard
```http
POST /api/flashcards/{flashcard_id}/add/
Authorization: Bearer <token>
Content-Type: application/json

{
    "word_id": 1
}
```

#### Get Flashcard Details
```http
GET /api/flashcards/{id}/
Authorization: Bearer <token>
```

---

### 🌐 Translation Endpoint

#### Translate Japanese Text
```http
POST /api/translate/
Content-Type: application/json

{
    "text": "こんにちは"
}
```

**Response:**
```json
{
    "translated": "Hello"
}
```

---

### 📜 History Endpoint

#### Get Search History
```http
GET /api/history/
Authorization: Bearer <token>
```

---

## 🏗 Architecture

### Project Structure
```
backend/
├── backend/                 # Django project settings
│   ├── settings.py         # Main configuration
│   ├── urls.py             # Root URL routing
│   └── wsgi.py             # WSGI entry point
│
├── core/                    # Main application
│   ├── api/                # API views/endpoints
│   │   ├── auth.py         # Authentication endpoints
│   │   ├── search.py       # Search functionality
│   │   ├── favorites.py    # Favorites management
│   │   ├── flashcards.py   # Flashcard CRUD
│   │   ├── history.py      # Search history
│   │   ├── jlpt.py         # JLPT word lists
│   │   ├── kanji.py        # Kanji details
│   │   ├── quiz.py         # AI quiz generation
│   │   ├── translate.py    # Translation service
│   │   └── urls.py         # API URL routing
│   │
│   ├── services/           # Business logic & external APIs
│   │   ├── jisho.py        # Jisho API integration
│   │   ├── tatoeba.py      # Tatoeba API integration
│   │   ├── kanji.py        # KanjiAPI integration
│   │   ├── quiz.py         # Gemini AI quiz generator
│   │   ├── ingest.py       # Data ingestion logic
│   │   └── history.py      # History service
│   │
│   ├── serializers/        # DRF serializers
│   │   ├── user.py         # User serializers
│   │   ├── word.py         # Word serializers
│   │   ├── favorite.py     # Favorite serializers
│   │   └── flashcard.py    # Flashcard serializers
│   │
│   ├── models.py           # Database models
│   └── admin.py            # Django admin config
│
├── manage.py               # Django CLI
├── .env                    # Environment variables
└── .env.example            # Environment template
```

### Database Schema

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│      User       │     │      Word       │     │   WordMeaning   │
├─────────────────┤     ├─────────────────┤     ├─────────────────┤
│ id              │     │ id              │     │ id              │
│ username        │     │ kanji           │     │ word_id (FK)    │
│ email           │     │ kana            │     │ meaning         │
│ password        │     │ parts_of_speech │     │ example_sentence│
│ role            │     │ jlpt_level      │     └────────┬────────┘
│ date_joined     │     │ is_cached       │              │
└────────┬────────┘     └────────┬────────┘              │
         │                       │              ┌────────▼────────┐
         │              ┌────────┴────────┐     │ ExampleSentence │
         │              │                 │     ├─────────────────┤
┌────────▼────────┐     │    ┌────────────▼──┐  │ id              │
│  SearchHistory  │     │    │   Favorite    │  │ meaning_id (FK) │
├─────────────────┤     │    ├───────────────┤  │ jp              │
│ id              │     │    │ id            │  │ en              │
│ user_id (FK)    │◄────┤    │ user_id (FK)  │  │ source          │
│ word_id (FK)    │─────┘    │ word_id (FK)  │  │ source_id       │
│ searched_at     │          └───────────────┘  └─────────────────┘
└─────────────────┘
                        ┌─────────────────┐     ┌─────────────────┐
                        │    Flashcard    │     │  FlashcardWord  │
                        ├─────────────────┤     ├─────────────────┤
                        │ id              │◄────│ flashcard_id(FK)│
                        │ user_id (FK)    │     │ word_id (FK)    │
                        │ name            │     └─────────────────┘
                        │ created_at      │
                        └─────────────────┘

┌─────────────────────┐
│ PasswordResetToken  │
├─────────────────────┤
│ id                  │
│ user_id (FK)        │
│ token               │
│ created_at          │
│ expires_at          │
│ is_used             │
└─────────────────────┘
```

### Data Flow

```
┌──────────┐     ┌──────────────┐     ┌─────────────┐
│  Client  │────▶│ Django REST  │────▶│   Postgre   │
│ (React)  │◀────│  Framework   │◀────│  Database   │
└──────────┘     └──────┬───────┘     └─────────────┘
                       │
         ┌─────────────┼─────────────┐
         │             │             │
         ▼             ▼             ▼
   ┌──────────┐  ┌──────────┐  ┌──────────┐
   │  Jisho   │  │ Tatoeba  │  │  Gemini  │
   │   API    │  │   API    │  │    AI    │
   └──────────┘  └──────────┘  └──────────┘
```

---

## 🔧 Key Technical Highlights

### 1. **Smart Caching Strategy**
- First searches local PostgreSQL database
- Falls back to external APIs only if not found
- Auto-caches new words for future requests
- Reduces API calls and improves response time

### 2. **N+1 Query Prevention**
- Uses Django's `prefetch_related` and `Prefetch` objects
- Optimizes database queries for nested relationships
- Ensures consistent response times

### 3. **Secure Password Reset Flow**
- UUID-based tokens with 1-hour expiration
- Single-use tokens (invalidated after use)
- Email notification via SMTP

### 4. **AI Integration with Rate Limiting**
- Exponential backoff retry mechanism for Gemini API
- Graceful handling of 429 (rate limit) errors
- JSON response parsing with fallback handling

### 5. **Performance Logging**
- Built-in timing logs for external API calls
- Easy identification of performance bottlenecks
- Configurable logging levels

---

## 🧪 Testing

```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test core
```

---

## 📄 License

This project is created for educational and portfolio purposes.

---
