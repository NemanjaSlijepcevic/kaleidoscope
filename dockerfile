ARG PYTHON_VERSION=3.13-alpine
FROM python:${PYTHON_VERSION} AS builder

# Prevents Python from writing pyc files to disk
ENV PYTHONDONTWRITEBYTECODE=1

#Prevents Python from buffering stdout and stderr
ENV PYTHONUNBUFFERED=1 

# Set the working directory in the container
WORKDIR /app

# Copy the requirements.txt file to the working directory
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Production stage
FROM python:${PYTHON_VERSION}

# Install gettext for translations
RUN apk add --no-cache gettext

# Copy the Python dependencies from the builder stage
COPY --from=builder /usr/local/lib/python3.13/site-packages/ /usr/local/lib/python3.13/site-packages/
COPY --from=builder /usr/local/bin/ /usr/local/bin/

# Set the working directory
WORKDIR /app

# Copy the rest of the application files
COPY . .

RUN python manage.py collectstatic --noinput && \
    python manage.py compilemessages

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 

# Expose the port the app runs on
EXPOSE 8000

# Start the application
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "kaleidoscope.wsgi:application"]
