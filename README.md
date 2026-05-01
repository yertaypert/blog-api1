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

The application will be available at `http://localhost`.

## 📖 API Documentation

The API is fully documented and browsable:

- **Swagger UI**: [http://localhost/api/docs/](http://localhost/api/docs/)
- **ReDoc**: [http://localhost/api/redoc/](http://localhost/api/redoc/)
- **OpenAPI Schema**: [http://localhost/api/schema/](http://localhost/api/schema/)

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
- **nginx**: Reverse proxy and static/media server (Port 80)
- **redis**: Cache and Broker (Port 6379)
- **celery_worker**: Background task processor
- **celery_beat**: Periodic task scheduler
- **flower**: Celery monitoring tool (Port 5555)

## Authentication

The API uses JWT (JSON Web Tokens). Obtain tokens at `/api/auth/token/` and include them in the `Authorization` header:
`Authorization: JWT <your_token>`

## Reverse Proxy Verification

After `docker compose up --build`, verify that requests go through nginx and that the app is not exposed directly on host port `8000`.

1. Admin route through nginx:
   ```bash
   curl -I http://localhost/admin/login/
   ```
   Expected:
   - `HTTP/1.1 200 OK`
   - `Server: nginx/...`

2. Static file through nginx:
   ```bash
   curl -I http://localhost/static/admin/css/base.css
   ```
   Expected:
   - `HTTP/1.1 200 OK`
   - a long `Cache-Control: max-age=...` header

3. API through nginx:
   ```bash
   curl http://localhost/api/posts/
   ```
   Expected:
   - JSON list of posts

4. Upstream failure is surfaced by nginx as `502`, not connection refused:
   ```bash
   docker compose stop web
   curl -I http://localhost/api/posts/
   ```
   Expected:
   - `HTTP/1.1 502 Bad Gateway`
   - response returned by nginx

   Restart `web` afterwards:
   ```bash
   docker compose start web
   ```

5. App container is not published directly to the host:
   ```bash
   curl http://localhost:8000/
   ```
   Expected:
   - connection refused

## WebSocket Verification

Use an existing published post slug such as `ws-test-post`.

1. Obtain a JWT:
   ```bash
   curl -sS -X POST http://localhost/api/auth/token/ \
     -H 'Content-Type: application/json' \
     -d '{"email":"ws-test@example.com","password":"StrongPass123!"}'
   ```

2. Connect with `wscat`:
   ```bash
   wscat -c "ws://localhost/ws/posts/ws-test-post/comments/?token=<JWT>"
   ```
   Expected:
   - WebSocket handshake succeeds with `101 Switching Protocols`

3. In another terminal, post a comment through the REST API:
   ```bash
   curl -sS -X POST http://localhost/api/posts/ws-test-post/comments/ \
     -H 'Content-Type: application/json' \
     -H 'Authorization: JWT <JWT>' \
     -d '{"body":"hello from curl"}'
   ```
   Expected:
   - `201 Created`
   - a WebSocket message arrives in `wscat`

4. Browser alternative:
   - Open DevTools and create a WebSocket connection to `ws://localhost/ws/posts/ws-test-post/comments/?token=<JWT>`
   - Post a comment via the REST API
   - Confirm the comment message arrives on the socket
