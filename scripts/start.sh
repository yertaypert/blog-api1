#!/bin/bash
set -e  # Exit immediately if a command fails
set -o pipefail
    
# ----------------------------------
# CONFIGURATION
# ----------------------------------
ENV_FILE=".env"
VENV_DIR=".venv"
DJANGO_MANAGE="python manage.py"
SUPERUSER_EMAIL="admin@example.com"
SUPERUSER_PASSWORD="admin123"
SUPERUSER_FIRST_NAME="Admin"
SUPERUSER_LAST_NAME="User"
SERVER_PORT=8000

# ----------------------------------
# FUNCTIONS
# ----------------------------------

echo_step() {
    echo
    echo "==== $1 ===="
}

check_env_vars() {
    echo_step "Checking environment variables"
    if [ ! -f "$ENV_FILE" ]; then
        echo "Error: $ENV_FILE file not found."
        exit 1
    fi

    # Load .env
    export $(grep -v '^#' $ENV_FILE | xargs)

    
    REQUIRED_VARS=("SECRET_KEY" "DEBUG" "EMAIL_BACKEND")

    MISSING_VARS=()
    for VAR in "${REQUIRED_VARS[@]}"; do
        if [ -z "${!VAR}" ]; then
            MISSING_VARS+=("$VAR")
        fi
    done

    if [ ${#MISSING_VARS[@]} -ne 0 ]; then
        echo "Error: Missing required environment variables:"
        for VAR in "${MISSING_VARS[@]}"; do
            echo "  - $VAR"
        done
        exit 1
    fi
    echo "All required environment variables are set."
}

create_virtualenv() {
    echo_step "Setting up virtual environment"
    if [ ! -d "$VENV_DIR" ]; then
        python3 -m venv $VENV_DIR
        echo "Virtualenv created at $VENV_DIR"
    fi
    # Activate venv
    source $VENV_DIR/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
}

run_migrations() {
    echo_step "Running database migrations"
    $DJANGO_MANAGE migrate
}

collect_static() {
    echo_step "Collecting static files"
    $DJANGO_MANAGE collectstatic --noinput
}

compile_translations() {
    echo_step "Compiling translation files"
    $DJANGO_MANAGE compilemessages || echo "No translation files found"
}

create_superuser() {
    echo_step "Creating superuser (if not exists)"
    python - <<END
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings.base')
django.setup()
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(email="$SUPERUSER_EMAIL").exists():
    User.objects.create_superuser(
        email="$SUPERUSER_EMAIL",
        first_name="$SUPERUSER_FIRST_NAME",
        last_name="$SUPERUSER_LAST_NAME",
        password="$SUPERUSER_PASSWORD"
    )
    print("Superuser created")
else:
    print("Superuser already exists")
END
}

seed_database() {
    echo_step "Seeding database with test data"
    $DJANGO_MANAGE loaddata scripts/fixtures/initial_data.json || echo "No fixture found, skipping seeding"
}

start_server() {
    echo_step "Starting Django development server"
    echo "API: http://127.0.0.1:$SERVER_PORT/api/"
    echo "Swagger UI: http://127.0.0.1:$SERVER_PORT/api/docs/"
    echo "ReDoc: http://127.0.0.1:$SERVER_PORT/api/redoc/"
    echo "Admin panel: http://127.0.0.1:$SERVER_PORT/admin/"
    echo "Superuser: $SUPERUSER_EMAIL / $SUPERUSER_PASSWORD"
    echo
    $DJANGO_MANAGE runserver 0.0.0.0:$SERVER_PORT
}

# ----------------------------------
# SCRIPT EXECUTION
# ----------------------------------
check_env_vars
create_virtualenv
run_migrations
collect_static
compile_translations
create_superuser
seed_database
start_server