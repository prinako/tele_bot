FROM python:3.10

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY bot.py .
COPY gemini.py .

CMD ["python", "bot.py"]