FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN addgroup --system app && adduser --system --ingroup app app

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

USER app

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
