# Events Platform - Backend API

A comprehensive Django-based events management platform with JWT authentication, role-based access control, and scheduled email notifications.

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

### Option 1: Running with Docker (Recommended)

#### Prerequisites

- Docker and Docker Compose installed
- Git

#### Steps

1. **Clone the repository**
  ```bash
   git clone <repository-url>
   cd django_assessment
  ```
2. **Configure environment variables**
   ```bash
   cp .env.example .env
   ```
   
   **For Docker setup**, the `.env` file should use Docker service names:
   ```env
   DATABASE_HOST=db
   REDIS_URL=redis://redis:6379/0
   CELERY_BROKER_URL=redis://redis:6379/0
   ```
   
   **Note:** The `.env.example` file is already configured for Docker. Just copy it and update the passwords if needed.
3. **Start all services with one command**
   ```bash
   ./start.sh
   ```
   
   Or manually:
   ```bash
   docker-compose up --build
   ```
   
   This will start:
   - PostgreSQL database (port 5433 on host, 5432 in container)
   - Redis (port 6379)
   - Django web server (port 8000)
   - Celery worker
   - Celery beat scheduler

4. **Setup PostgreSQL database (if needed)**
   
   If the database doesn't exist or you need to create it manually:
   
   ```bash
   # Access PostgreSQL container
   docker-compose exec db psql -U postgres
   
   # Inside PostgreSQL shell, create database and user
   CREATE DATABASE events_db;
   CREATE USER postgres WITH PASSWORD '123456';
   GRANT ALL PRIVILEGES ON DATABASE events_db TO postgres;
   
   # Exit PostgreSQL shell
   \q
   ```
   
   **Note:** The credentials should match those in your `.env` file:
   - `DATABASE_NAME=events_db`
   - `DATABASE_USER=postgres`
   - `DATABASE_PASSWORD=123456`

5. **Run database migrations**
   ```bash
   docker-compose exec web python manage.py migrate
   ```

6. **Access the application**
   - API: [http://localhost:8000](http://localhost:8000)
   - Admin panel: [http://localhost:8000/admin](http://localhost:8000/admin)

7. **Create a superuser (optional)**
   ```bash
   docker-compose exec web python manage.py createsuperuser
   ```

8. **Useful Docker commands**
   ```bash
   # View logs
   docker-compose logs -f web
   
   # Run tests
   docker-compose exec web pytest
   
   # Django shell
   docker-compose exec web python manage.py shell
   
   # Stop services
   docker-compose down
   
   # Stop and remove volumes (clean slate)
   docker-compose down -v
   ```

---

### Option 2: Running without Docker (Virtual Environment)

#### Prerequisites

- Python 3.12 or higher
- PostgreSQL 15 installed and running
- Redis installed and running
- Git

#### Steps

1. **Clone the repository**
  ```bash
   git clone <repository-url>
   cd django_assessment
  ```
2. **Create and activate virtual environment**
  ```bash
   # Create virtual environment
   python3 -m venv venv

   # Activate virtual environment
   # On Linux/Mac:
   source venv/bin/activate
   # On Windows:
   # venv\Scripts\activate
  ```
3. **Install dependencies**
  ```bash
   # Install production dependencies
   pip install -e .

   # Install development dependencies (optional)
   pip install -e ".[dev]"
  ```
4. **Configure environment variables**
  ```bash
   cp .env.example .env
  ```
   Edit `.env` and update the following for local setup:
5. **Setup PostgreSQL database**
  ```bash
   psql -U postgres
   CREATE DATABASE events_platform_db;
   \q
  ```
6. **Create logs directory**
  ```bash
   mkdir -p logs
  ```
7. **Run database migrations**
  ```bash
   python manage.py migrate
  ```
8. **Create superuser (optional)**
  ```bash
   python manage.py createsuperuser
  ```
9. **Start the development server**
  ```bash
   python manage.py runserver
  ```
   The API will be available at: [http://localhost:8000](http://localhost:8000)
10. **Start Celery worker (in a new terminal)**
  ```bash
    # Activate virtual environment first
    source venv/bin/activate

    # Start Celery worker
    celery -A events_platform worker -l info
  ```
11. **Start Celery Beat scheduler (in another terminal)**
  ```bash
    # Activate virtual environment first
    source venv/bin/activate

    # Start Celery Beat
    celery -A events_platform beat -l info
  ```

## Environment Variables


| Variable                | Description                   | Default                | Required       |
| ----------------------- | ----------------------------- | ---------------------- | -------------- |
| `DEBUG`                 | Enable debug mode             | `False`                | No             |
| `SECRET_KEY`            | Django secret key             | -                      | Yes            |
| `ALLOWED_HOSTS`         | Comma-separated allowed hosts | `localhost,127.0.0.1`  | Yes            |
| `DATABASE_NAME`         | PostgreSQL database name      | `events_db`            | Yes            |
| `DATABASE_USER`         | PostgreSQL username           | `events_user`          | Yes            |
| `DATABASE_PASSWORD`     | PostgreSQL password           | `events_password`      | Yes            |
| `DATABASE_HOST`         | PostgreSQL host               | `db`                   | Yes            |
| `DATABASE_PORT`         | PostgreSQL port               | `5432`                 | Yes            |
| `REDIS_URL`             | Redis connection URL          | `redis://redis:6379/0` | Yes            |
| `EMAIL_BACKEND`         | Django email backend          | `console` (dev)        | Yes            |
| `EMAIL_HOST`            | SMTP server host              | `smtp.gmail.com`       | For production |
| `EMAIL_PORT`            | SMTP server port              | `587`                  | For production |
| `EMAIL_HOST_USER`       | SMTP username                 | -                      | For production |
| `EMAIL_HOST_PASSWORD`   | SMTP password/app password    | -                      | For production |
| `EMAIL_USE_TLS`         | Use TLS for email             | `True`                 | For production |
| `DEFAULT_FROM_EMAIL`    | Default sender email          | -                      | Yes            |
| `CELERY_BROKER_URL`     | Celery broker URL             | `redis://redis:6379/0` | Yes            |
| `CELERY_RESULT_BACKEND` | Celery result backend         | `redis://redis:6379/0` | Yes            |


### Email Configuration

For development, emails are printed to console. For production:

1. Use Gmail with App Password:
  - Enable 2FA on your Google account
  - Generate App Password: [https://myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)
  - Set `EMAIL_HOST_USER` and `EMAIL_HOST_PASSWORD`
2. Or use SendGrid, Mailgun, etc.

## API Endpoints

### Authentication


| Method | Endpoint             | Description              | Auth Required |
| ------ | -------------------- | ------------------------ | ------------- |
| POST   | `/auth/signup`       | Register new user        | No            |
| POST   | `/auth/verify-email` | Verify email with OTP    | No            |
| POST   | `/auth/login`        | Login and get JWT tokens | No            |
| POST   | `/auth/refresh`      | Refresh access token     | No            |
| POST   | `/auth/resend-otp`   | Resend OTP email         | No            |


### Events (Seeker)


| Method | Endpoint          | Description                | Auth Required |
| ------ | ----------------- | -------------------------- | ------------- |
| GET    | `/events/search/` | Search events with filters | Seeker        |


**Query Parameters**:

- `location` - Filter by location (case-insensitive contains)
- `language` - Filter by language (exact match)
- `starts_after` - Events starting after datetime (ISO 8601)
- `starts_before` - Events starting before datetime (ISO 8601)
- `q` - Search in title/description
- `page` - Page number for pagination

### Enrollments (Seeker)


| Method | Endpoint                 | Description               | Auth Required  |
| ------ | ------------------------ | ------------------------- | -------------- |
| POST   | `/enrollments/`          | Enroll in an event        | Seeker         |
| GET    | `/enrollments/`          | List all enrollments      | Seeker         |
| GET    | `/enrollments/past/`     | List past enrollments     | Seeker         |
| GET    | `/enrollments/upcoming/` | List upcoming enrollments | Seeker         |
| GET    | `/enrollments/{id}/`     | Get enrollment details    | Seeker (owner) |


### Events (Facilitator)


| Method    | Endpoint                    | Description       | Auth Required       |
| --------- | --------------------------- | ----------------- | ------------------- |
| POST      | `/facilitator/events/`      | Create event      | Facilitator         |
| GET       | `/facilitator/events/`      | List my events    | Facilitator         |
| GET       | `/facilitator/events/{id}/` | Get event details | Facilitator (owner) |
| PUT/PATCH | `/facilitator/events/{id}/` | Update event      | Facilitator (owner) |
| DELETE    | `/facilitator/events/{id}/` | Delete event      | Facilitator (owner) |


## Running Tests

### With Docker

```bash
# Run all tests
docker-compose exec web pytest

# Run with coverage report
docker-compose exec web pytest --cov=. --cov-report=html

# Run specific test file
docker-compose exec web pytest authentication/tests/test_signup.py

# Run specific test class
docker-compose exec web pytest authentication/tests/test_signup.py::TestSignup
```

### Without Docker (Virtual Environment)

```bash
# Activate virtual environment first
source venv/bin/activate

# Run all tests
pytest

# Run with coverage report
pytest --cov=. --cov-report=html

# Run specific test file
pytest authentication/tests/test_signup.py

# Run specific test class
pytest authentication/tests/test_signup.py::TestSignup

# Run with verbose output
pytest -v

# Run tests matching a pattern
pytest -k "test_signup"
```

### View Coverage Report

```bash
# Coverage report is generated in htmlcov/index.html
open htmlcov/index.html        # Mac
xdg-open htmlcov/index.html    # Linux
start htmlcov/index.html       # Windows
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

## Troubleshooting

### With Docker

**Database connection errors:**

```bash
docker-compose restart db
docker-compose logs db
```

**Celery tasks not running:**

```bash
docker-compose logs celery
docker-compose logs celery-beat
docker-compose restart celery celery-beat
```

**Migrations not applied:**

```bash
docker-compose exec web python manage.py migrate
```

**View logs:**

```bash
docker-compose logs -f web              # Follow web logs
docker-compose logs --tail=100 web      # Last 100 lines
docker-compose logs -f celery           # Follow Celery logs
```

**Clean restart:**

```bash
docker-compose down -v                  # Remove all containers and volumes
docker-compose up --build               # Rebuild and start
```

---

### Without Docker (Virtual Environment)

**Database connection errors:**

```bash
# Check if PostgreSQL is running
sudo systemctl status postgresql        # Linux
brew services list                      # Mac

# Restart PostgreSQL
sudo systemctl restart postgresql       # Linux
brew services restart postgresql        # Mac

# Test connection
psql -U your_user -d events_platform_db
```

**Celery tasks not running:**

```bash
# Check if Redis is running
redis-cli ping                          # Should return PONG

# Restart Redis
sudo systemctl restart redis            # Linux
brew services restart redis             # Mac

# Check Celery worker logs (if running in background)
# Kill and restart Celery
pkill -f "celery worker"
celery -A events_platform worker -l info

# Kill and restart Celery Beat
pkill -f "celery beat"
celery -A events_platform beat -l info
```

**Migrations not applied:**

```bash
source venv/bin/activate
python manage.py migrate
```

**View application logs:**

```bash
# Logs are stored in logs/ directory
tail -f logs/events_platform.log        # Follow application logs
tail -f logs/errors.log                 # Follow error logs

# View Django development server logs
# (displayed in terminal where runserver is running)
```

**Module not found errors:**

```bash
# Reinstall dependencies
source venv/bin/activate
pip install -e ".[dev]"
```

**Port already in use:**

```bash
# Find process using port 8000
lsof -i :8000                           # Mac/Linux
netstat -ano | findstr :8000            # Windows

# Kill the process
kill -9 <PID>                           # Mac/Linux
taskkill /PID <PID> /F                  # Windows

# Or use a different port
python manage.py runserver 8001
```

**Permission denied errors:**

```bash
# Fix logs directory permissions
chmod -R 755 logs/

# Fix virtual environment permissions
chmod -R 755 venv/
```

---

## Quick Command Reference


| Task                    | With Docker                                                | Without Docker (venv)                      |
| ----------------------- | ---------------------------------------------------------- | ------------------------------------------ |
| **Start application**   | `./start.sh` or `docker-compose up`                        | `python manage.py runserver`               |
| **Stop application**    | `docker-compose down`                                      | `Ctrl+C`                                   |
| **Run tests**           | `docker-compose exec web pytest`                           | `pytest`                                   |
| **Run migrations**      | `docker-compose exec web python manage.py migrate`         | `python manage.py migrate`                 |
| **Create superuser**    | `docker-compose exec web python manage.py createsuperuser` | `python manage.py createsuperuser`         |
| **Django shell**        | `docker-compose exec web python manage.py shell`           | `python manage.py shell`                   |
| **View logs**           | `docker-compose logs -f web`                               | `tail -f logs/events_platform.log`         |
| **Format code**         | `docker-compose exec web black .`                          | `black .`                                  |
| **Run linter**          | `docker-compose exec web flake8`                           | `flake8`                                   |
| **Start Celery worker** | (Auto-started with docker-compose)                         | `celery -A events_platform worker -l info` |
| **Start Celery Beat**   | (Auto-started with docker-compose)                         | `celery -A events_platform beat -l info`   |


---

## Additional Resources

- **Postman Collection**: Import `postman_collection.json` for API testing
- **API Testing Guide**: See `API_TESTING_GUIDE.md` for comprehensive testing instructions
- **Requirements Validation**: See `REQUIREMENTS_VALIDATION.md` for compliance details
- **Project Status**: See `PROJECT_STATUS.md` for current status and deployment info

