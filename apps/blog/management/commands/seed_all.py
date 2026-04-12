# Python modules
import random

# Django modules
from django.core.management.base import BaseCommand
from django.utils.text import slugify

# Project modules
from apps.users.models import User
from apps.blog.models import Post, Comment, Category


class Command(BaseCommand):
    help = "Seed the database with users, categories, posts, and comments for testing."

    def handle(self, *args, **kwargs):
        self.stdout.write("Seeding database...")

        # -----------------------------
        # Users
        # -----------------------------
        users = []
        if not User.objects.exists():
            for i in range(1, 6):
                user = User.objects.create_user(
                    email=f"user{i}@example.com",
                    first_name=f"User{i}",
                    last_name="Test",
                    password="secret123",
                    preferred_language=random.choice(["en", "ru", "kk"]),
                    preferred_timezone="Asia/Almaty"
                )
                users.append(user)
                self.stdout.write(self.style.SUCCESS(f"Created user: {user.email}"))
        else:
            users = list(User.objects.all())
            self.stdout.write(self.style.WARNING("Users already exist, using existing ones."))

        # -----------------------------
        # Categories
        # -----------------------------
        categories_data = [
            {"en": "Tech", "ru": "Техника", "kk": "Техника"},
            {"en": "Lifestyle", "ru": "Образ жизни", "kk": "Өмір салты"},
            {"en": "News", "ru": "Новости", "kk": "Жаңалықтар"},
        ]

        categories = []
        for data in categories_data:
            cat, created = Category.objects.get_or_create(
                slug=slugify(data["en"]),
                defaults={
                    "name_en": data["en"],
                    "name_ru": data["ru"],
                    "name_kk": data["kk"],
                }
            )
            categories.append(cat)
            if created:
                self.stdout.write(self.style.SUCCESS(f"Created category: {cat.name_en}"))
            else:
                self.stdout.write(self.style.WARNING(f"Category exists: {cat.name_en}"))

        # -----------------------------
        # Posts
        # -----------------------------
        for i in range(1, 21):
            author = random.choice(users)
            status = random.choice([Post.Status.PUBLISHED, Post.Status.DRAFT])
            category = random.choice(categories)

            post = Post.objects.create(
                title=f"Seed Post {i}",
                slug=f"seed-post-{i}",
                body=f"This is the body of seed post {i}. Lorem ipsum dolor sit amet.",
                author=author,
                status=status,
                category=category
            )
            self.stdout.write(self.style.SUCCESS(f"Created post: {post.slug} (status={status})"))

            # -----------------------------
            # Comments
            # -----------------------------
            num_comments = random.randint(1, 3)
            for j in range(num_comments):
                comment_author = random.choice(users)
                Comment.objects.create(
                    post=post,
                    author=comment_author,
                    body=f"This is comment {j+1} on post {i}."
                )

        self.stdout.write(self.style.SUCCESS("Database seeding complete!"))