import os
from decouple import config, Config, RepositoryEnv, Csv



BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Load .env
env_path = os.path.join(BASE_DIR, '.env')
config = Config(RepositoryEnv(env_path))


# Environment
ENV_ID = config("BLOG_ENV_ID", default="local")
SECRET_KEY = config("BLOG_SECRET_KEY")
DEBUG = config("BLOG_DEBUG", default=False, cast=bool)
ALLOWED_HOSTS = config("BLOG_ALLOWED_HOSTS", default="localhost", cast=Csv())

# Redis
REDIS_URL = config("BLOG_REDIS_URL", default="redis://127.0.0.1:6379/1")

# Email
EMAIL_BACKEND = config(
    "BLOG_EMAIL_BACKEND",
    default="django.core.mail.backends.console.EmailBackend"
)