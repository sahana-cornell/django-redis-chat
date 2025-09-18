# Django Redis Chat

A real-time chat application built with **Python**, **Django**, **Django Channels**, **Redis**, and **WebSockets**.

It supports user signup/login with JWT authentication, creating conversations, and exchanging real-time messages.

Includes API throttling, monitoring via Prometheus, and GitHub Actions CI.

---

## Features

• **User management:** Signup, login, JWT authentication

• **Conversations:** Create/list conversations

• **Real-time chat:** Messages sent/received via WebSockets

• **Redis:** Fast in-memory store for chat messages

• **Database (Postgres):** Persistent store for users & conversation metadata

• **API throttling:** Rate limits on signup, login, conversations, and message reads

• **Monitoring:** `/metrics` endpoint for Prometheus

• **CI/CD:** GitHub Actions workflow runs tests automatically

---

## Getting Started

### 1. Clone the repo

```bash
git clone https://github.com/<your-username>/django-redis-chat.git
cd django-redis-chat
```

### 2. Start services with Docker

```bash
docker compose up --build
```

This will start:

• `web`: Django app (Uvicorn + Channels)
• `db`: Postgres
• `redis`: Redis

### 3. Apply database migrations

```bash
docker compose exec web python manage.py migrate
```

---

## Usage

### Signup

```bash
curl -X POST http://localhost:8000/api/users/signup \
-H "Content-Type: application/json" \
-d '{"first_name":"Test","last_name":"User","email":"test@example.com","password":"Pass1243!"}'
```

### Login & Get Token

```bash
curl -X POST http://localhost:8000/api/users/token \
-H "Content-Type: application/json" \
-d '{"username":"test@example.com","password":"Pass1243!"}'
```

### Create Conversation

```bash
curl -X POST http://localhost:8000/api/chat/conversations \
-H "Authorization: Bearer <ACCESS_TOKEN>" \
-H "Content-Type: application/json" -d '{}'
```

---

## WebSocket Messaging

Use a WebSocket client (or the included `index.html` demo):

```
ws://localhost:8000/ws/chat/<conversation_id>/?token=<ACCESS_TOKEN>
```

---

## Monitoring

Prometheus metrics are exposed at:

```
http://localhost:8000/metrics
```

Examples:

• `django_http_requests_total_by_method_total`
• `django_http_responses_total_by_status_total`

---

## Tests

Run the full test suite:

```bash
docker compose exec web pytest
```

---

## CI/CD

This project includes GitHub Actions (`.github/workflows/ci.yml`) to automatically run tests on push.

Add the badge to the top of this README:

```markdown
![CI](https://github.com/<your-username>/django-redis-chat/actions/workflows/ci.yml/badge.svg)
```

---

## Throttling Rules

• **Signup:** 2/min
• **Login:** 5/min
• **Conversations:** 5/min
• **Message reads:** 10/min
• **Anonymous:** 20/min
• **Authenticated user (overall):** 120/min

---

## Tech Stack

• **Backend:** Django 5 + Django REST Framework + Django Channels
• **Auth:** SimpleJWT
• **Realtime:** Redis + Channels layers
• **Database:** PostgreSQL
• **Container:** Docker Compose
• **Monitoring:** Prometheus
• **CI/CD:** GitHub Actions

---

## Project Structure

```
django-redis-chat/
├── chat/                           # Chat app (models, consumers, views)
├── users/                          # User app (signup, auth)
├── config/                         # Django project settings
├── tests/                          # Pytest test suite
├── templates/                      # Static demo (chat.html)
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── README.md
└── .github/workflows/ci.yml
```

---

## Deployment

Local use with Docker is supported.

For cloud deployment:

• Add environment variables in `docker-compose.override.yml` or GitHub Secrets.
• Use Heroku, GCP, AWS, or Azure to deploy containers.

---

## Author

Built by **Sahana Vrinda Kakarla** (Cornell Engineering Management, M.Eng 2025).