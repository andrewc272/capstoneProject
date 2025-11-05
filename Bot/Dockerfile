FROM python:3.11-slim

ENV SCRIPT=cliPlayer.py

WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . .

CMD ["sh", "-c", "python $SCRIPT"]



