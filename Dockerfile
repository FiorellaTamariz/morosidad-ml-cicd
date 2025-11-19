FROM python:3.11-slim

LABEL maintainer="fiorellatamarizpantoja@gmail.com"
LABEL description="API de predicción de morosidad - Norte Andino SAC"

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/
COPY models/ ./models/
COPY data/ ./data/

EXPOSE 5000

CMD ["python", "src/app.py"]