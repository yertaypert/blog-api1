# Blog API

Django-based blog API featuring real-time notifications, asynchronous statistics, and background task processing.

## Features

- **Core Blog**: Full CRUD for Posts and Comments with slug-based lookups.
- **Real-time Notifications**: WebSocket and SSE support for live updates.
- **Async Statistics**: Concurrent external API fetching for exchange rates and local time.
- **Background Tasks**: Celery workers for cache invalidation and email processing.
- **Performance**: Multi-layered caching with Redis and optimized database queries.
- **API Documentation**: Fully interactive Swagger and ReDoc documentation.
- **Localization**: Multi-language support (EN, RU, KK) with timezone-aware responses.

## 🛠 Tech Stack

- **Framework**: Django 6.0 (ASGI via Daphne)
- **API**: Django Rest Framework (DRF)
- **Database**: SQLite3 (Persistent via Docker volumes)
- **Task Queue**: Celery + Redis
- **Documentation**: drf-spectacular (OpenAPI 3.0)
- **Containerization**: Docker & Docker Compose

## Quick Start

### Prerequisites
- Docker and Docker Compose installed.

### Setup & Run
1. **Clone the repository**:
   ```bash
   git clone <repo-url>
   cd project1
   ```

2. **Configure environment**:
   ```bash
   cp settings/.env.example settings/.env
   # Edit settings/.env if necessary
   ```

3. **Start the services**:
   ```bash
   docker compose up --build
   ```

The application will be available at `http://localhost:8000`.

## 📖 API Documentation

The API is fully documented and browsable:

- **Swagger UI**: [http://localhost:8000/api/docs/](http://localhost:8000/api/docs/)
- **ReDoc**: [http://localhost:8000/api/redoc/](http://localhost:8000/api/redoc/)
- **OpenAPI Schema**: [http://localhost:8000/api/schema/](http://localhost:8000/api/schema/)

### Key API Endpoints

| Category | Method | Endpoint | Description |
| :--- | :--- | :--- | :--- |
| **Auth** | `POST` | `/api/auth/register/` | Register a new user account |
| **Auth** | `POST` | `/api/auth/token/` | Login and obtain JWT tokens |
| **Auth** | `PATCH` | `/api/auth/preferences/` | Update user language/timezone |
| **Posts** | `GET` | `/api/posts/` | List all published posts (cached) |
| **Posts** | `POST` | `/api/posts/` | Create a new post (Auth required) |
| **Posts** | `GET` | `/api/posts/{slug}/` | Retrieve a single post by slug |
| **Comments**| `GET` | `/api/posts/{slug}/comments/`| List comments for a post |
| **Comments**| `POST`| `/api/posts/{slug}/comments/`| Add a comment (Auth required) |
| **Stats** | `GET` | `/api/stats/` | Real-time blog & market stats |
| **Notifs** | `GET` | `/api/notifications/` | List user notifications |

## 🏗 Services


- **web**: Django Daphne server (Port 8000)
- **redis**: Cache and Broker (Port 6379)
- **celery_worker**: Background task processor
- **celery_beat**: Periodic task scheduler
- **flower**: Celery monitoring tool (Port 5555)

## Authentication

The API uses JWT (JSON Web Tokens). Obtain tokens at `/api/auth/token/` and include them in the `Authorization` header:
`Authorization: JWT <your_token>`
