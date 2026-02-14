import os
from decouple import config, Config, RepositoryEnv


# 1. Get the absolute path to the directory containing this file (settings/)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 2. Point specifically to the .env file inside this folder
env_path = os.path.join(BASE_DIR, '.env')
config = Config(RepositoryEnv(env_path))


ENV_ID = config("BLOG_ENV_ID", default="local")

SECRET_KEY = config("BLOG_SECRET_KEY")

DEBUG = config("BLOG_DEBUG", default=False, cast=bool)