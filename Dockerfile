FROM python:3.11-slim

WORKDIR /app

# Создаем пользователя для запуска приложения
RUN useradd -m botuser && \
    chown -R botuser:botuser /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Устанавливаем права на папку для базы данных
RUN mkdir -p /app/data && \
    chown -R botuser:botuser /app/data

USER botuser

CMD ["python", "main.py"] 