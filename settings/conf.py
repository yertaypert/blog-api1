from decouple import config

ENV_ID = config("BLOG_ENV_ID", default="local")

SECRET_KEY = config("BLOG_SECRET_KEY")

DEBUG = config("BLOG_DEBUG", default=False, cast=bool)