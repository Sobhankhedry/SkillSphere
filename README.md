# 🌐 SkillSphere — Microservices & Real-Time Skill Exchange Platform

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Django REST Framework](https://img.shields.io/badge/Django_REST_Framework-4.2+-092E20?style=for-the-badge&logo=django&logoColor=white)](https://www.django-rest-framework.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Redis](https://img.shields.io/badge/Redis-7+-DC382D?style=for-the-badge&logo=redis&logoColor=white)](https://redis.io/)
[![Celery](https://img.shields.io/badge/Celery-5+-37B24D?style=for-the-badge&logo=celery&logoColor=white)](https://docs.celeryq.dev/)
[![Docker](https://img.shields.io/badge/Docker-Enabled-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](LICENSE)

SkillSphere is a production-ready, highly scalable Backend service built to facilitate peer-to-peer skill exchange, interactive messaging, real-time notifications, and automated booking workflows. 

Designed with asynchronous event handling, background processing, caching layers, and containerized deployment, SkillSphere demonstrates modern backend engineering practices and clean architecture principles.

---

## 🏗 System Architecture & Technology Stack

```
                     +---------------------------------------+
                     |             Client / Web              |
                     +---------------------------------------+
                                         |
                                  [ REST / WS ]
                                         v
                     +---------------------------------------+
                     |         Nginx / Reverse Proxy         |
                     +---------------------------------------+
                                         |
                                  [ WSGI / ASGI ]
                                         v
                     +---------------------------------------+
                     |       Django REST Framework           |
                     |  (Authentication, API, WebSockets)    |
                     +---------------------------------------+
                       /                 |                 \
         [ SQL Queries ]           [ Cache / Broker ]      [ Async Tasks ]
               /                         |                         \
              v                          v                          v
    +------------------+       +------------------+       +------------------+
    | PostgreSQL DB    |       |   Redis Cache    |       |  Celery Workers  |
    | (Primary Storage)|       |  & PubSub Engine |       | & Beat Scheduler |
    +------------------+       +------------------+       +------------------+
```

### Core Technologies
* **Framework:** Python 3.11, Django 4.x, Django REST Framework (DRF)
* **Real-time Protocol:** Django Channels, WebSockets, ASGI
* **Database & Persistence:** PostgreSQL, Django ORM
* **Caching & Broker:** Redis (Caching, Session Management, Channel Layer)
* **Asynchronous Tasks:** Celery, Celery Beat (Scheduled Jobs & Notifications)
* **Containerization:** Docker, Docker Compose
* **Authentication:** JWT (JSON Web Tokens) via SimpleJWT
* **Testing:** Pytest / Django Test Suite

---

## ✨ Core Features

* 🔐 **Authentication & Authorization:** Secure JWT-based auth with refresh token rotation and role-based access control (RBAC).
* 🔄 **Real-Time Messaging:** WebSocket-enabled peer-to-peer chat with persistent message history and delivery status.
* ⚡ **Asynchronous Background Processing:** Offloaded email delivery, audit logging, and periodic scheduling using Celery & Redis.
* 🚀 **Performant Caching Layer:** Optimized database queries and response latency through Redis-backed caching strategies.
* 📅 **Booking & Session Scheduler:** Transactional booking flow for skill exchange sessions with conflict resolution.
* 🐳 **Fully Containerized:** Multi-container setup orchestrating Application, Database, Redis, and Celery services with Docker Compose.

---

## 📁 Project Structure

```
SkillSphere/
├── apps/
│   ├── authentication/     # User models, JWT auth, profiles
│   ├── skills/             # Skill catalogs, categories, matching
│   ├── bookings/           # Session booking logic, scheduling
│   ├── chat/               # WebSockets consumers, real-time messaging
│   └── notifications/      # Async email/push notification services
├── core/
│   ├── settings/           # Modular settings (base, dev, prod)
│   ├── asgi.py             # ASGI entry point for WebSockets
│   └── wsgi.py             # WSGI entry point
├── docker/                 # Container Dockerfiles and startup scripts
├── tests/                  # Integration and Unit tests
├── docker-compose.yml      # Orchestration file
├── requirements.txt        # Python dependencies
├── .env.example            # Environment variables template
└── README.md
```

---

## 🚀 Quickstart & Installation

### Prerequisites
* [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed on your machine.
* [Git](https://git-scm.com/) installed.

### Running with Docker Compose (Recommended)

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/Sobhankhedry/SkillSphere.git
   cd SkillSphere
   ```

2. **Configure Environment Variables:**
   ```bash
   cp .env.example .env
   ```
   *Edit `.env` to configure your passwords, secret keys, and database credentials.*

3. **Build and Run Containers:**
   ```bash
   docker-compose up -d --build
   ```

4. **Apply Migrations & Create Superuser:**
   ```bash
   docker-compose exec web python manage.py migrate
   docker-compose exec web python manage.py createsuperuser
   ```

5. **Access Services:**
   * **REST API:** `http://localhost:8000/api/v1/`
   * **Swagger Docs:** `http://localhost:8000/api/docs/`
   * **Admin Panel:** `http://localhost:8000/admin/`

---

## 📖 API Endpoints & Documentation

SkillSphere provides interactive API documentation generated via **drf-spectacular / Swagger UI**.

| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/v1/auth/register/` | Register a new user | ❌ No |
| `POST` | `/api/v1/auth/login/` | JWT token acquisition | ❌ No |
| `GET` | `/api/v1/skills/` | List and search skills | ❌ No |
| `POST` | `/api/v1/bookings/` | Request a skill-exchange session | 🔒 Yes |
| `GET` | `/api/v1/chat/rooms/` | Get user chat rooms | 🔒 Yes |
| `WS` | `/ws/chat/<room_id>/` | Real-time WebSocket chat connection | 🔒 Yes |

---

## 🧪 Testing

To run the automated unit and integration test suite inside the Docker container:

```bash
docker-compose exec web pytest
```

Or using Django's default test runner:
```bash
docker-compose exec web python manage.py test
```

---

## 🛡 Security & Best Practices

* **Environment Separation:** Sensitive configuration keys are loaded strictly from `.env` files.
* **Database Transactions:** Atomic operations are implemented using `transaction.atomic()` for critical booking sequences.
* **CORS & CSRF:** Strict CORS headers configured for frontend interaction.

---

## 📜 License

Distributed under the MIT License. See `LICENSE` for more information.

---

👨‍💻 **Developed by [Sobhan Khedry](https://github.com/Sobhankhedry)**  
*Backend Engineer | Python & .NET Enthusiast*
