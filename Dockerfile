FROM python:3.12-slim

# Opt
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Working dir
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gettext \
    redis-tools \
    && rm -rf /var/lib/apt/lists/*

# Create a non-root user and set up app directory
RUN useradd -m appuser && mkdir -p /app/data /app/staticfiles /app/media \ && chown -R appuser:appuser /app

# Copy requirements
COPY requirements/base.txt /app/requirements/base.txt

# Upgrade pip and install requirements
RUN pip install --upgrade pip && pip install -r /app/requirements/base.txt

# Copy the rest of the project
COPY . /app/

# Ensure permissions are correct after copying files
RUN chown -R appuser:appuser /app

# Nonroot user, least privliege
USER appuser

# Writable dirs
RUN mkdir -p /app/staticfiles /app/media /app/data

# Port
EXPOSE 8000

ENTRYPOINT ["./scripts/entrypoint.sh"]
