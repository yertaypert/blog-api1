FROM python:3.12-slim

# Opt
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Working dir
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gettext \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements/base.txt /app/requirements/base.txt

# Upgrade pip and install requirements
RUN pip install --upgrade pip && pip install -r /app/requirements/base.txt

# Copy the rest of the project
COPY . /app/

# Nonroot user, least privliege
USER appuser

# Port
EXPOSE 8000


ENTRYPOINT ["./scripts/entrypoint.sh"]
