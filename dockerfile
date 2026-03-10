ARG PYTHON_VERSION=3.13-alpine
FROM python:${PYTHON_VERSION} AS builder

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install build dependencies (needed for Pillow and similar packages)
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
    libffi-dev

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

FROM python:${PYTHON_VERSION}

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install runtime libraries + gettext
RUN apk add --no-cache \
    jpeg \
    zlib \
    freetype \
    lcms2 \
    openjpeg \
    tiff \
    gettext

WORKDIR /app

# Copy installed Python packages from builder
COPY --from=builder /usr/local/lib/python3.13/site-packages/ /usr/local/lib/python3.13/site-packages/
COPY --from=builder /usr/local/bin/ /usr/local/bin/

# Copy project files
COPY . .

# Compile static files and translations
RUN python manage.py collectstatic --noinput && \
    python manage.py compilemessages

EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "kaleidoscope.wsgi:application"]
