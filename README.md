# Task Manager API

A RESTful API built with Django REST Framework for managing tasks across teams and workspaces.

## Tech Stack
- Python 3.12 / Django 5 / Django REST Framework
- PostgreSQL
- JWT Authentication (SimpleJWT)
- Celery + Redis (async notifications)
- Docker

## Features
- Multi-workspace support with role-based access (Admin / Member / Viewer)
- Project and task management with status, priority, due dates
- Task assignment with email notifications
- Activity log — full history of changes
- API documentation via Swagger (drf-spectacular)

## Getting Started

### 1. Clone the repo
git clone https://github.com/your-username/taskmanager-api.git
cd taskmanager-api

### 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

### 3. Install dependencies
pip install -r requirements.txt

### 4. Set up environment variables
cp .env.example .env
# Edit .env with your database credentials

### 5. Run migrations
python manage.py migrate

### 6. Start the server
python manage.py runserver