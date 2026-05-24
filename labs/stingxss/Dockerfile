FROM python:3.12-slim

RUN apt-get update \
 && apt-get install -y --no-install-recommends chromium \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .
COPY core/ core/
COPY templates/ templates/

ENV FLASK_ENV=production
EXPOSE 80

CMD ["python", "app.py"]
