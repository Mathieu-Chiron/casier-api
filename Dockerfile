FROM python:3.11-slim

RUN pip install fastapi uvicorn playwright redis

ENV PLAYWRIGHT_BROWSERS_PATH=/app/playwright
RUN playwright install-deps chromium
RUN playwright install chromium

WORKDIR /app
COPY . .

CMD uvicorn main:app --host 0.0.0.0 --port ${PORT:-8080}
