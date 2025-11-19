FROM python:3.10-alpine

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_APP=app.py

WORKDIR /app

RUN apk update && apk add --no-cache build-base libffi-dev openssl-dev

COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . .

RUN if [ ! -f .env ]; then python -c "from secrets import token_hex; open('.env', 'w').write('SECRET_KEY=' + token_hex(32))"; fi

EXPOSE 5001

CMD ["flask", "run", "--host=0.0.0.0"]

