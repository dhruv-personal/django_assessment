# Prompt Log - Events Platform Development

This document contains all prompts used during the development of the Django Events Platform backend application.

---

## Prompt 1: Initial Planning & Architecture

```
I need you to act as an expert backend Django developer. I have a backend assessment that requires building an Events Platform API with the following specifications:

**Role**: Expert Django Backend Developer with deep knowledge of:
- Django 5.x and Django REST Framework
- JWT authentication patterns
- Role-based access control (RBAC)
- PostgreSQL database design
- Celery for asynchronous tasks
- Docker containerization
- Production-ready code practices

**Task**: Use Plan Mode to create a comprehensive implementation plan for:

### Core Requirements:
1. **Authentication System**
   - Email-based signup (NO username field)
   - 6-digit OTP email verification with 5-minute TTL
   - Attempt limits on OTP verification
   - JWT tokens (access + refresh)
   - Default Django User model (cannot be swapped)

2. **Role-Based Access Control**
   - Two roles: Seeker and Facilitator
   - Enforce using DRF permissions
   - All endpoints must check role AND ownership

3. **Domain Models**
   - Event: title, description, language, location, start/end times, capacity, creator
   - Enrollment: event, seeker, status, timestamps
   - Constraint: No duplicate enrollments

4. **Seeker Features**
   - Search events with filters (location, language, date range, query)
   - Pagination and ordering (upcoming first)
   - Enroll in events (respect capacity)
   - List past and upcoming enrollments

5. **Facilitator Features**
   - CRUD operations on events
   - Only creator can update/delete
   - View enrollment statistics (total enrollments, available seats)

6. **Database Requirements**
   - PostgreSQL preferred
   - Proper indexes on: starts_at, language, location
   - Migrations included

7. **Bonus Features** (to be implemented):
   - Dockerized project
   - Scheduled email notifications:
     * Follow-up email: 1 hour after enrollment
     * Reminder email: 1 hour before event starts

**Before creating the plan, please ask me any clarifying questions about:**
- Email backend preferences (SMTP, console, etc.)
- Testing framework choice
- JWT token expiration times
- Celery broker preference
- Django version specifics
- Project naming conventions
- Any architectural decisions

Once I answer your questions, create a detailed implementation plan breaking down:
- Project structure
- Model design with relationships
- API endpoints specification
- Authentication flow
- Permission strategy
- Celery task design
- Docker setup
- Testing approach

Please use Plan Mode for this.
```

---

## Prompt 2: Implementation

```
Perfect! I've reviewed the plan and answered all your questions. The plan looks comprehensive and well-structured.

Now, please implement the entire project based on the plan you created. 

**Implementation Guidelines:**
- Follow the plan strictly - don't skip any components
- Create all files with production-ready code
- Implement proper error handling
- Add comprehensive docstrings
- Follow Django and DRF best practices
- Ensure all models, serializers, views, and URLs are properly connected
- Set up Docker with all required services (PostgreSQL, Redis, Celery, Celery Beat)
- Include pytest tests for all major functionality
- Create a Postman collection for API testing

**Do NOT:**
- Generate irrelevant markdown files
- Make assumptions - if something is unclear, ask
- Skip any features from the requirements

Please implement everything systematically, marking TODOs as you progress.
```

---

## Prompt 3: Code Quality & Architecture Improvements

```
Great work on the implementation! Now I need you to refactor and enhance the codebase to follow production-grade standards. Please make the following improvements across the entire project:

### Dependency Management
- Use `pyproject.toml` instead of `requirements.txt`
- Configure all tools (black, isort, pytest, coverage) in pyproject.toml
- Add proper project metadata

### CORS Configuration
- Add `django-cors-headers` to the project
- Configure CORS settings in `settings.py`
- Add CORS configuration to environment variables (.env and .env.example)
- Provide both development and production-ready CORS settings

### Docker Optimization
- Use a lightweight Python Docker image (python:3.11-slim or similar)
- Optimize Dockerfile for production use
- Ensure proper build caching

### API Response Standardization
- Implement custom middleware for consistent response format across ALL endpoints
- All success responses should follow the same structure
- All error responses should follow the same structure
- Middleware should handle both DRF views and standard Django views

### Import Conventions
- Fix ALL imports across the application to use explicit absolute imports
- Change `from .models import Model` to `from app_name.models import Model`
- Apply this to: models, serializers, views, utils, tasks, signals
- Ensure consistency across authentication/, events/, and events_platform/

### Pre-commit Hooks
- Implement `.pre-commit-config.yaml`
- Configure hooks for:
  * Black (code formatting)
  * isort (import sorting)
  * flake8 (linting)
  * Other code quality checks
- Ensure hooks run automatically on git commit

### View Architecture
- Convert ALL function-based views to class-based views
- Use appropriate base classes: APIView, ViewSet, ModelViewSet, generics
- No function-based views should remain in the codebase

### Logging System
- Implement file-based rotating logs (RotatingFileHandler)
- Configure proper log levels
- Add logging to key operations (authentication, enrollment, errors)
- Add `logs/` directory to .gitignore
- Create logs directory structure

### Constants Management
- Create a global constants file at `events_platform/constants.py`
- Move ALL static values to constants:
  * Email templates (OTP, follow-up, reminder)
  * User roles
  * Enrollment statuses
  * OTP settings (expiry time, max attempts)
  * Error codes
- Update all files to import from constants

### DRF Optimization
- Review all views and optimize to use generics or viewsets appropriately
- Use ModelViewSet where full CRUD is needed
- Use specific generics (ListAPIView, CreateAPIView) where only specific operations are needed
- Don't compromise functionality - use both where needed

### Documentation
- Keep `PROMPT_LOG.md` empty for now - I'll fill it later
- Ensure README is comprehensive
- Include all configuration details

Please make ALL these changes systematically across the entire codebase. Don't skip any files or any improvements.
```

---

## Prompt 4: Dependency Version Management

```
In the `pyproject.toml` file, I want absolute package versions with NO backward compatibility.

Currently, dependencies use version specifiers like:
- `Django>=5.0,<6.0`
- `djangorestframework>=3.14`
- `pytest>=7.4`

Please change ALL package versions to use exact version pinning with `==`:
- Use `==` operator for all dependencies (both production and dev)
- Pin to the exact versions currently installed in the virtual environment
- This applies to ALL packages in both `dependencies` and `optional-dependencies.dev` sections
- Ensure no package uses `>=`, `~=`, or version ranges

This ensures reproducible builds and prevents unexpected updates from breaking the application in production.
```

---

## Prompt 5: Comprehensive Setup Documentation

```
Update the README.md to provide clear setup instructions for BOTH Docker and non-Docker (virtual environment) approaches.

### For Docker Setup Section:
- Provide step-by-step instructions
- Include how to access the PostgreSQL container
- Show how to manually create the database using `docker-compose exec`
- Specify exact credentials from .env file
- Include the SQL commands to run inside the PostgreSQL container:
  * CREATE DATABASE
  * CREATE USER  
  * GRANT PRIVILEGES
- Add note about port mapping (5433 on host, 5432 in container)
- Explain Docker service names (db, redis) for internal communication

### For Virtual Environment Setup Section:
- Complete instructions from scratch
- How to create and activate venv
- How to install dependencies using `pip install -e .` and `pip install -e ".[dev]"`
- Configure .env for local development (using localhost instead of Docker service names)
- How to set up local PostgreSQL database
- How to set up local Redis
- How to run Django development server
- How to run Celery worker and Celery Beat separately
- Include all Django management commands (migrate, createsuperuser, runserver)

### Additional Requirements:
- Add a comparison table showing equivalent commands for Docker vs venv
- Include troubleshooting sections for both approaches
- Mention where to find OTP codes in development (console logs)
- Add sections for running tests in both environments
- Include quick command reference

Make it comprehensive enough that anyone (with or without Docker experience) can set up and run the project successfully.
```

