FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app ./app

ENV DATABASE_URL=sqlite:////data/payroll_ops.db
ENV CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
EXPOSE 8000
VOLUME ["/data"]
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
