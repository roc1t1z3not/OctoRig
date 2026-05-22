FROM python:3.11-slim
WORKDIR /app
RUN pip install --no-cache-dir flask==3.0.3
COPY . .
RUN mkdir -p /data/uploads
EXPOSE 5000
CMD ["python", "app.py"]
