# SkillSphere – Learning & Project Collaboration Platform

A production-ready backend built with Django 5, Django REST Framework, PostgreSQL, Redis, Celery, and Django Channels.

## Architecture

Follows Domain Driven Design (DDD) with Hexagonal Architecture (Ports & Adapters) and Clean Architecture principles.

```
skillsphere/
├── config/                    # Django project configuration
│   ├── settings/              # Base, Development, Production settings
│   ├── celery.py              # Celery application
│   ├── urls.py                # Root URL configuration
│   └── asgi.py                # ASGI for WebSocket support
├── domain/                    # Domain layer (enums, value objects)
│   └── enums.py               # Domain enums
├── apps/                      # Bounded contexts
│   ├── users/                 # User management & authentication
│   ├── projects/              # Projects, files, comments
│   ├── notifications/         # Notifications (DB + WebSocket)
│   ├── analytics/             # Dashboard analytics
│   ├── activity_logs/         # Activity tracking middleware
│   └── search/                # Full-text search
├── tests/                     # Test suite
├── docker-compose.yml         # Docker orchestration
├── Dockerfile                 # Application container
└── requirements/              # Python dependencies
```

## Setup

### Prerequisites

- Python 3.13+
- PostgreSQL 16+
- Redis 7+
- Docker & Docker Compose (optional)

### Quick Start with Docker

```bash
cp .env.example .env
docker-compose up -d
docker-compose exec django python manage.py migrate
docker-compose exec django python manage.py createsuperuser
```

### Manual Setup

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
pip install -r requirements/development.txt
cp .env.example .env  # Edit with your settings
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

### Running Celery

```bash
celery -A config worker -l info
celery -A config beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
```

## API Endpoints

Base URL: `http://localhost:8000/api/v1/`

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/register/` | Register new user |
| POST | `/auth/login/` | Login (JWT token pair) |
| POST | `/auth/token/refresh/` | Refresh access token |
| POST | `/auth/logout/` | Logout (blacklist refresh token) |

### Users
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/users/profiles/me/` | Get current user profile |
| PATCH | `/users/profiles/me/` | Update profile |
| GET | `/users/profiles/by_username/?username=X` | Get profile by username |

### Projects
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/projects/` | List public projects |
| POST | `/projects/` | Create project |
| GET | `/projects/{id}/` | Get project detail |
| PUT/PATCH | `/projects/{id}/` | Update project |
| DELETE | `/projects/{id}/` | Delete project |
| GET | `/projects/my_projects/` | List user's projects |
| GET | `/projects/{id}/files/` | List project files |
| POST | `/projects/{id}/upload_file/` | Upload file to project |
| GET | `/projects/{id}/download/{file_id}/` | Download project file |

### Comments
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/comments/?project={id}` | List comments for project |
| POST | `/comments/` | Create comment |
| PUT/PATCH | `/comments/{id}/` | Update comment |
| DELETE | `/comments/{id}/` | Delete comment |

### Notifications
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/notifications/` | List notifications |
| GET | `/notifications/unread_count/` | Get unread count |
| PATCH | `/notifications/{id}/mark_read/` | Mark as read |
| PATCH | `/notifications/mark_all_read/` | Mark all as read |

### Dashboard
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/dashboard/user/` | User dashboard metrics |
| GET | `/dashboard/admin/` | Admin dashboard metrics |

### Search
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/search/?q={query}` | Global search |
| GET | `/search/projects/?q={query}` | Search projects |
| GET | `/search/users/?q={query}` | Search users |

## WebSocket

Connect to `ws://localhost:8000/ws/notifications/` for real-time notifications.

## Testing

```bash
pytest
pytest --cov=apps --cov-report=html
```

## Documentation

- Swagger UI: `http://localhost:8000/api/docs/`
- OpenAPI Schema: `http://localhost:8000/api/schema/`
