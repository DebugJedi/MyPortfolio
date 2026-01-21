# MyPortfolio

Professional web application built with FastAPI.

## Quick Start

```bash
# Setup
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Configure
cp .env.example .env
# Edit .env with your settings

# Run
python app/main.py
```

Visit: http://localhost:8080

## Features

- ✅ Modern FastAPI backend
- ✅ SQLAlchemy database integration
- ✅ Professional project structure
- ✅ Analytics tracking
- ✅ API documentation at /api/docs

## Project Structure

```
MyPortfolio/
├── app/           # Application code
├── static/        # Static assets
├── templates/     # HTML templates
├── tests/         # Tests
└── alembic/       # Database migrations
```

## Development

```bash
# Run with auto-reload
python app/main.py

# Run tests
pytest

# Database migrations
alembic revision --autogenerate -m "description"
alembic upgrade head
```
