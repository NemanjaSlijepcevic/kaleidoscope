ARG PYTHON_VERSION=3.13-alpine
FROM python:${PYTHON_VERSION} AS builder

# Prevent .pyc files & enable unbuffered output
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install build dependencies for packages like Pillow
RUN apk add --no-cache \
    gcc \
    musl-dev \
    jpeg-dev \
    zlib-dev \
    freetype-dev \
    lcms2-dev \
    openjpeg-dev \
    tiff-dev \
    tk-dev \
    tcl-dev \
    libffi-dev \
    gettext-dev \
    gettext

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV DJANGO_SETTINGS_MODULE=kaleidoscope.settings
RUN python manage.py compilemessages

FROM python:${PYTHON_VERSION}

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apk add --no-cache \
    jpeg \
    zlib \
    freetype \
    lcms2 \
    openjpeg \
    tiff \
    gettext \
    bash

COPY --from=builder /usr/local/lib/python3.13/site-packages/ /usr/local/lib/python3.13/site-packages/
COPY --from=builder /usr/local/bin/ /usr/local/bin/

COPY --from=builder /app /app

ENV DJANGO_SETTINGS_MODULE=kaleidoscope.settings

EXPOSE 8000

CMD python manage.py collectstatic --noinput && \
    gunicorn --bind 0.0.0.0:8000 --workers 3 kaleidoscope.wsgi:application
