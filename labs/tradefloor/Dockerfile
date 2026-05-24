FROM python:3.11-slim
WORKDIR /app
RUN pip install --no-cache-dir flask==3.0.3 lxml==5.2.2
COPY . .
RUN mkdir -p /data
EXPOSE 80
CMD ["python", "app.py"]
