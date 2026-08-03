FROM python:3.13-slim
#base image
ENV PYTHONDONTWRITEBYTECODE=1
#won't allow creating .pyc
ENV PYTHONUNBUFFERED=1
#sending all the oututs and logs to terminal
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libpq-dev && \
    rm -rf /var/lib/apt/lists/*
# installing library for postgres sql
COPY requirements/ ./requirements/
RUN pip install --no-cache-dir -r requirements/production.txt

COPY . .
# copy all the files incontainer
RUN adduser --disabled-password --gecos '' appuser && \
    mkdir -p /app/media /app/staticfiles && chown -R appuser:appuser /app/media /app/staticfiles
USER appuser
# adding user for security
EXPOSE 8000
# container on port 8000 listening
CMD ["sh", "-c", "python manage.py migrate && python manage.py collectstatic --noinput && gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 4"]
