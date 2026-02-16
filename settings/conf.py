import os
from decouple import config, Config, RepositoryEnv



BASE_DIR = os.path.dirname(os.path.abspath(__file__))


env_path = os.path.join(BASE_DIR, '.env')
config = Config(RepositoryEnv(env_path))


ENV_ID = config("BLOG_ENV_ID", default="local")

SECRET_KEY = config("BLOG_SECRET_KEY")

DEBUG = config("BLOG_DEBUG", default=False, cast=bool)