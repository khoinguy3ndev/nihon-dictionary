FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies for psycopg2
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Collect static files (optional)
RUN python manage.py collectstatic --noinput || true

# Render requires using $PORT, not hardcoded 8000
CMD ["gunicorn", "backend.wsgi:application", "--bind", "0.0.0.0:${PORT}"]
