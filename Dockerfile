FROM python:3-alpine3.22

ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .

RUN apk add --no-cache --virtual .build-deps gcc musl-dev \
    && pip install --no-cache-dir --disable-pip-version-check -r requirements.txt \
    && find /usr/local -type d -name 'tests' -exec rm -rf {} + \
    && find /usr/local -type d -name '__pycache__' -exec rm -rf {} + \
    && apk del .build-deps

COPY src/ .

CMD ["python3", "tuya_exporter.py"]