# Use Alpine Linux base
FROM python:3.10-alpine

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_APP=app.py

# Set working directory
WORKDIR /app

# Install OS dependencies (for pip, flask, etc.)
RUN apk update && apk add --no-cache \
    build-base \
    libffi-dev \
    openssl-dev

# Copy requirements and install them
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy app code
COPY . .

# Generate .env with a SECRET_KEY during image build
RUN python -c "from secrets import token_hex; open('.env', 'w').write('SECRET_KEY=' + token_hex(32))"

# Expose Flask's default port
EXPOSE 5000


# Default command (you can override in docker-compose or CLI)
CMD ["flask", "run", "--host=0.0.0.0"]


