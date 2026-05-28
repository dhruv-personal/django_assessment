# Events Platform - Backend API

A comprehensive Django-based events management platform with JWT authentication, role-based access control, and scheduled email notifications.

## Table of Contents

- [Overview](#overview)
- [Tech Stack](#tech-stack)
- [Features](#features)
- [Setup Instructions](#setup-instructions)
- [Environment Variables](#environment-variables)
- [API Endpoints](#api-endpoints)
- [Running Tests](#running-tests)
- [Design Decisions](#design-decisions)
- [Tradeoffs](#tradeoffs)

## Overview

This platform enables two types of users:
- **Seekers**: Can search for events, enroll in events, and view their past/upcoming enrollments
- **Facilitators**: Can create, update, delete events and view enrollment statistics

## Tech Stack

- **Framework**: Django 5.x
- **API**: Django REST Framework
- **Authentication**: JWT (djangorestframework-simplejwt)
- **Database**: PostgreSQL 15
- **Task Queue**: Celery with Redis broker
- **Containerization**: Docker & Docker Compose
- **Testing**: pytest with pytest-django

## Features

### Authentication
- Email-based signup (no username required)
- OTP email verification (6-digit code, 5-minute expiry)
- JWT-based authentication (Access token: 15 min, Refresh token: 7 days)
- Token refresh and blacklist support

### Role-Based Access Control (RBAC)
- Two roles: Seeker and Facilitator
- Permission-based endpoint access
- Ownership verification for CRUD operations

### Event Management
- Facilitators can create, update, delete events
- Events include: title, description, language, location, timing, capacity
- Enrollment tracking with available seats calculation

### Event Search & Filtering (Seeker)
- Filter by: location, language, date range
- Search by: title or description (query parameter `q`)
- Pagination (25 items per page)
- Ordered by start time (upcoming first)

### Enrollment System
- Seekers can enroll in events
- Capacity enforcement with race condition prevention
- Duplicate enrollment prevention
- View past and upcoming enrollments

### Scheduled Emails (Celery)
- **Follow-up email**: Sent 1 hour after enrollment
- **Reminder email**: Sent 1 hour before event starts (periodic task every 10 minutes)

### Database Optimizations
- Indexes on: `starts_at`, `language`, `location`
- Composite indexes for common query patterns
- Unique constraints for data integrity

## Setup Instructions

### Prerequisites
- Docker and Docker Compose installed
- Git

### Local Development Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd django_assessment
   ```

2. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration (see Environment Variables section)
   ```

3. **Build and start services**
   ```bash
   docker-compose up --build
   ```

   This will start:
   - PostgreSQL database (port 5432)
   - Redis (port 6379)
   - Django web server (port 8000)
   - Celery worker
   - Celery beat scheduler

4. **Access the application**
   - API: http://localhost:8000
   - Admin panel: http://localhost:8000/admin

5. **Create a superuser (optional)**
   ```bash
   docker-compose exec web python manage.py createsuperuser
   ```

## Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `DEBUG` | Enable debug mode | `True` | No |
| `SECRET_KEY` | Django secret key | - | Yes |
| `ALLOWED_HOSTS` | Comma-separated allowed hosts | `localhost,127.0.0.1` | Yes |
| `DATABASE_NAME` | PostgreSQL database name | `events_db` | Yes |
| `DATABASE_USER` | PostgreSQL username | `events_user` | Yes |
| `DATABASE_PASSWORD` | PostgreSQL password | `events_password` | Yes |
| `DATABASE_HOST` | PostgreSQL host | `db` | Yes |
| `DATABASE_PORT` | PostgreSQL port | `5432` | Yes |
| `REDIS_URL` | Redis connection URL | `redis://redis:6379/0` | Yes |
| `EMAIL_BACKEND` | Django email backend | `console` (dev) | Yes |
| `EMAIL_HOST` | SMTP server host | `smtp.gmail.com` | For production |
| `EMAIL_PORT` | SMTP server port | `587` | For production |
| `EMAIL_HOST_USER` | SMTP username | - | For production |
| `EMAIL_HOST_PASSWORD` | SMTP password/app password | - | For production |
| `EMAIL_USE_TLS` | Use TLS for email | `True` | For production |
| `DEFAULT_FROM_EMAIL` | Default sender email | - | Yes |
| `CELERY_BROKER_URL` | Celery broker URL | `redis://redis:6379/0` | Yes |
| `CELERY_RESULT_BACKEND` | Celery result backend | `redis://redis:6379/0` | Yes |

### Email Configuration

For development, emails are printed to console. For production:

1. Use Gmail with App Password:
   - Enable 2FA on your Google account
   - Generate App Password: https://myaccount.google.com/apppasswords
   - Set `EMAIL_HOST_USER` and `EMAIL_HOST_PASSWORD`

2. Or use SendGrid, Mailgun, etc.

## API Endpoints

### Authentication

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/auth/signup` | Register new user | No |
| POST | `/auth/verify-email` | Verify email with OTP | No |
| POST | `/auth/login` | Login and get JWT tokens | No |
| POST | `/auth/refresh` | Refresh access token | No |
| POST | `/auth/resend-otp` | Resend OTP email | No |

### Events (Seeker)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/events/search/` | Search events with filters | Seeker |

**Query Parameters**:
- `location` - Filter by location (case-insensitive contains)
- `language` - Filter by language (exact match)
- `starts_after` - Events starting after datetime (ISO 8601)
- `starts_before` - Events starting before datetime (ISO 8601)
- `q` - Search in title/description
- `page` - Page number for pagination

### Enrollments (Seeker)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/enrollments/` | Enroll in an event | Seeker |
| GET | `/enrollments/` | List all enrollments | Seeker |
| GET | `/enrollments/past/` | List past enrollments | Seeker |
| GET | `/enrollments/upcoming/` | List upcoming enrollments | Seeker |
| GET | `/enrollments/{id}/` | Get enrollment details | Seeker (owner) |

### Events (Facilitator)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/facilitator/events/` | Create event | Facilitator |
| GET | `/facilitator/events/` | List my events | Facilitator |
| GET | `/facilitator/events/{id}/` | Get event details | Facilitator (owner) |
| PUT/PATCH | `/facilitator/events/{id}/` | Update event | Facilitator (owner) |
| DELETE | `/facilitator/events/{id}/` | Delete event | Facilitator (owner) |

### Response Formats

**Pagination**:
```json
{
  "count": 100,
  "next": "http://localhost:8000/events/search/?page=2",
  "previous": null,
  "results": [...]
}
```

**Error**:
```json
{
  "detail": "Error message",
  "code": "error_code"
}
```

## Running Tests

### Run all tests
```bash
docker-compose exec web pytest
```

### Run with coverage report
```bash
docker-compose exec web pytest --cov=. --cov-report=html
```

### Run specific test file
```bash
docker-compose exec web pytest authentication/tests/test_signup.py
```

### Run specific test class
```bash
docker-compose exec web pytest authentication/tests/test_signup.py::TestSignup
```

### View coverage report
```bash
# Coverage report is generated in htmlcov/index.html
open htmlcov/index.html  # Mac
xdg-open htmlcov/index.html  # Linux
```

## Design Decisions

### 1. UserProfile Instead of Custom User Model
**Decision**: Use Django's default User model with a OneToOne UserProfile.

**Reasoning**: The requirement explicitly states "You must use Django's default User model (do not swap it)". While a custom user model would be cleaner, we worked within the constraint by:
- Using email as username during signup
- Storing role and verification status in UserProfile
- Auto-creating profile via Django signals

### 2. OTP Storage in Database
**Decision**: Store OTPs in PostgreSQL instead of Redis.

**Reasoning**:
- Persistent audit trail of OTP attempts
- Easier to implement attempt limiting and expiry
- Simpler deployment (one less dependency consideration)
- **Tradeoff**: Slightly slower than Redis, but acceptable for OTP verification use case

### 3. Celery for Scheduled Emails
**Decision**: Use Celery with Celery Beat for email scheduling.

**Reasoning**:
- Industry-standard for async tasks in Django
- Reliable task execution with retry mechanisms
- Scalable for future background tasks
- **Tradeoff**: More complex than django-cron, but more robust for production

### 4. Index Choices
**Decision**: Added indexes on `starts_at`, `language`, `location`, and composite indexes.

**Reasoning**:
- `starts_at`: Primary filter for upcoming events (most common query)
- `language`/`location`: Common filter criteria in search
- Composite indexes: Optimize combined filter queries
- **Tradeoff**: Increased write time and storage, but justified by read performance gains

### 5. Race Condition Prevention in Enrollment
**Decision**: Use `select_for_update()` for capacity checks.

**Reasoning**:
- Prevents double-booking when multiple users enroll simultaneously
- Database-level locking ensures consistency
- **Tradeoff**: Slight performance impact under high concurrency, but necessary for data integrity

### 6. JWT Token Rotation
**Decision**: Enable token rotation and blacklisting.

**Reasoning**:
- Security: Old refresh tokens are invalidated
- Logout support through blacklist
- **Tradeoff**: Additional database queries, but essential for security

## Tradeoffs

### 1. Email as Username
**Issue**: Using email as username creates a unique constraint on both fields.

**Solution**: Normalize email to lowercase during signup.

**Tradeoff**: Cannot have separate username and email identity, but meets requirement.

### 2. Stateless JWT vs Database Sessions
**Choice**: JWT with token rotation.

**Pros**: 
- Scalable (no session storage)
- Works across multiple servers
- Mobile-friendly

**Cons**:
- Cannot immediately revoke access tokens (must wait for expiry)
- Larger request size

**Mitigation**: Short access token lifetime (15 minutes) + refresh token blacklist.

### 3. Capacity Enforcement
**Challenge**: Race conditions when checking available seats.

**Solution**: Database-level locking with `select_for_update()`.

**Tradeoff**: Reduced concurrency under high load vs data accuracy. We chose accuracy.

### 4. Email Backend Configuration
**Development**: Console backend (prints emails to terminal)

**Production**: SMTP backend (requires configuration)

**Reasoning**: Easier local testing without SMTP setup, but requires explicit production configuration.

### 5. Pagination Size
**Choice**: 25 items per page.

**Reasoning**: Balance between:
- Fewer API calls (larger pages)
- Faster response times (smaller pages)
- Mobile data usage

**Future**: Could make this configurable per client.

## Project Structure

```
django_assessment/
├── events_platform/          # Django project settings
│   ├── settings.py          # Main configuration
│   ├── celery.py           # Celery configuration
│   └── urls.py             # Root URL configuration
├── authentication/          # Auth app
│   ├── models.py           # UserProfile, OTP models
│   ├── serializers.py      # Auth serializers
│   ├── views.py            # Auth endpoints
│   ├── permissions.py      # RBAC permissions
│   ├── utils.py            # OTP utilities
│   └── tests/              # Auth tests
├── events/                  # Events app
│   ├── models.py           # Event, Enrollment models
│   ├── serializers.py      # Event serializers
│   ├── views.py            # Event endpoints
│   ├── filters.py          # Search filters
│   ├── permissions.py      # Event permissions
│   ├── tasks.py            # Celery tasks
│   └── tests/              # Event tests
├── docker-compose.yml       # Docker orchestration
├── Dockerfile              # Container image
├── requirements.txt        # Python dependencies
├── pytest.ini              # Test configuration
├── .env                    # Environment variables
└── README.md               # This file
```

## Development Workflow

1. Make code changes
2. Run tests: `docker-compose exec web pytest`
3. Check for errors: `docker-compose logs web`
4. Run migrations: `docker-compose exec web python manage.py migrate`
5. Access shell: `docker-compose exec web python manage.py shell`

## Stopping the Application

```bash
docker-compose down          # Stop containers
docker-compose down -v       # Stop and remove volumes (clears database)
```

## Troubleshooting

### Database connection errors
```bash
docker-compose restart db
docker-compose logs db
```

### Celery tasks not running
```bash
docker-compose logs celery
docker-compose logs celery-beat
docker-compose restart celery celery-beat
```

### Migrations not applied
```bash
docker-compose exec web python manage.py migrate
```

### View logs
```bash
docker-compose logs -f web     # Follow web logs
docker-compose logs --tail=100 web  # Last 100 lines
```

## License

This project is created for assessment purposes.