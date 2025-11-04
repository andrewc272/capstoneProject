# Use Alpine Linux base
FROM python:3.11-slim

ENV SCRIPT=cliPlayer.py

# Set working directory
WORKDIR /app

# Copy requirements and install them
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy app code
COPY . .

# Default command (you can override in docker-compose or CLI)
CMD ["sh", "-c", "python $SCRIPT"]


