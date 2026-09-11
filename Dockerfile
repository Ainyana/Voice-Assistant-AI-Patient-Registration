FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["sh", "-c", "exec uvicorn app.main:app --host 127.0.0.1 --port ${PORT:-8000}"]
