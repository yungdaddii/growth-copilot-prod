.PHONY: help install dev build up down logs clean test migrate

help:
	@echo "Available commands:"
	@echo "  make install   - Install dependencies"
	@echo "  make dev       - Start development servers"
	@echo "  make build     - Build Docker images"
	@echo "  make up        - Start all services with Docker"
	@echo "  make down      - Stop all Docker services"
	@echo "  make logs      - Show Docker logs"
	@echo "  make clean     - Clean up containers and volumes"
	@echo "  make test      - Run tests"
	@echo "  make migrate   - Run database migrations"

install:
	cd backend && pip install -r requirements.txt
	cd frontend && npm install

dev:
	@echo "Starting development servers..."
	@echo "Backend: http://localhost:8000"
	@echo "Frontend: http://localhost:3000"
	docker-compose up postgres redis -d
	cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
	cd frontend && npm run dev

build:
	docker-compose build

up:
	docker-compose up -d
	@echo "Services started!"
	@echo "Frontend: http://localhost:3000"
	@echo "Backend: http://localhost:8000"
	@echo "API Docs: http://localhost:8000/docs"

down:
	docker-compose down

logs:
	docker-compose logs -f

clean:
	docker-compose down -v
	rm -rf backend/__pycache__
	rm -rf backend/.pytest_cache
	rm -rf frontend/.next
	rm -rf frontend/node_modules

test:
	cd backend && pytest tests/

migrate:
	cd backend && alembic upgrade head

init-db:
	cd backend && alembic init migrations
	cd backend && alembic revision --autogenerate -m "Initial migration"
	cd backend && alembic upgrade head