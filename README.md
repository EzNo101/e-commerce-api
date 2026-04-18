# E-Commerce API

Production-inspired backend API for an e-commerce domain, built with FastAPI and asynchronous SQLAlchemy.

The project focuses on clean architecture boundaries, authentication with rotating JWT refresh tokens, order checkout flow with Stripe PaymentIntent, and containerized local development with Docker Compose.

## Table of Contents

- [Overview](#overview)
- [Core Features](#core-features)
- [Tech Stack](#tech-stack)
- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [Environment Variables](#environment-variables)
- [Run Locally](#run-locally)
- [Run with Docker](#run-with-docker)
- [Database Migrations](#database-migrations)
- [API Surface](#api-surface)
- [Security Notes](#security-notes)
- [Architectural Decisions](#architectural-decisions)

## Overview

This API covers the most common e-commerce backend modules:

- User registration and authentication
- Product and category catalog management
- Cart operations
- Order checkout lifecycle
- Stripe payment integration with webhook handling

The codebase uses an application/service/repository split with explicit Unit of Work orchestration and domain-level exceptions.

## Core Features

- Auth with JWT access + refresh tokens
- HTTP-only auth cookies for token transport
- Refresh token rotation with Redis-backed token store
- Role-aware access checks (`active`/`admin` users)
- Category and product CRUD flows
- Cart item add/update/remove/clear
- Checkout from cart to order
- Stripe PaymentIntent creation
- Stripe signed webhook verification
- Order/payment status transitions based on webhook events
- Alembic migrations
- Dockerized local environment (`api`, `db`, `redis`)

## Tech Stack

### Backend

- Python 3.12
- FastAPI
- SQLAlchemy 2.x (async)
- asyncpg
- Pydantic v2 + pydantic-settings
- Uvicorn

### Auth and Security

- python-jose (JWT)
- passlib + bcrypt (password hashing)
- Cookie-based auth transport (`httponly`, `secure`, `samesite`)

### Data and Integrations

- PostgreSQL
- Redis
- Stripe SDK

### Tooling and Infrastructure

- Alembic
- Docker + Docker Compose

## Architecture

The project follows a layered structure with clear responsibilities:

- API layer (`app/api`)
	- Declares routes, validates input, maps domain errors to HTTP responses.
- Service layer (`app/services`)
	- Contains business use-cases (auth, cart, order, payment workflows).
- Repository layer (`app/repositories`)
	- Encapsulates persistence and query logic.
- Domain/model layer (`app/models`, `app/schemas`)
	- SQLAlchemy entities and Pydantic I/O schemas.
- Infrastructure (`app/db`, `app/core`, `app/utils`)
	- Database session, Unit of Work, configuration, security, cookies, app lifespan.

### Request Flow (Typical)

1. FastAPI endpoint receives request.
2. Dependencies resolve current user/UoW/session.
3. Service executes business logic.
4. Repository performs data operations.
5. Unit of Work commits or rolls back.
6. API layer returns DTO/response model.

## Project Structure

```text
app/
	api/           # Route handlers (auth, users, cart, products, categories, orders)
	core/          # Settings, dependencies, lifespan, security
	db/            # Engine/session setup, Redis client, Unit of Work, token store
	models/        # SQLAlchemy models
	repositories/  # Data access layer
	schemas/       # Request/response DTOs
	services/      # Business logic
	utils/         # Cookie helpers and utility logic
alembic/         # Database migrations
Dockerfile
docker-compose.yml
```

## Environment Variables

Copy and fill from `.env.example`:

```bash
cp .env.example .env
```

Main variables:

- `DATABASE_URL`
- `SECRET_KEY`
- `ACCESS_TOKEN_EXPIRE_MINUTES`
- `REFRESH_TOKEN_EXPIRE_DAY`
- `ALGORITHM`
- `STRIPE_SECRET_KEY`
- `STRIPE_PUBLISHABLE_KEY`
- `STRIPE_WEBHOOK_SECRET`
- `REDIS_URL`
- `CACHE_TTL`
- `DEBUG`

## Run Locally

### 1) Create virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2) Install dependencies

```bash
pip install -r requirements.txt
```

### 3) Configure environment

```bash
cp .env.example .env
```

### 4) Run migrations

```bash
alembic upgrade head
```

### 5) Start API

```bash
uvicorn app.main:app --reload
```

API docs: `http://localhost:8000/docs`

## Run with Docker

### 1) Build and start

```bash
docker compose up -d --build
```

### 2) Apply migrations

```bash
docker compose exec api alembic upgrade head
```

### 3) Open API docs

`http://localhost:8000/docs`

### 4) Useful commands

```bash
docker compose ps
docker compose logs -f api
docker compose down
docker compose down -v
```

## Database Migrations

Create a new migration:

```bash
alembic revision --autogenerate -m "describe_change"
```

Apply migrations:

```bash
alembic upgrade head
```

Rollback one step:

```bash
alembic downgrade -1
```

## API Surface

High-level route groups:

- `/auth` - register/login/refresh/logout
- `/users` - profile read/update, password change
- `/category` - category operations
- `/products` - catalog operations
- `/cart` - cart operations
- `/orders` - order listing/details/checkout
- `/orders/webhook/stripe` - Stripe webhook endpoint

## Security Notes

- Passwords are stored as bcrypt hashes.
- Access and refresh tokens are JWT-based.
- Refresh tokens are rotated and tracked in Redis via `jti`.
- Stripe webhooks are validated with signature verification.
- Authentication cookies are sent as HTTP-only.

For production hardening, consider:

- Strict CORS policy
- Secret management via vault or cloud secret manager
- HTTPS everywhere
- Token/cookie policy review for frontend deployment domain

## Architectural Decisions

### 1) Repository + Service + UoW separation

Persistence concerns are isolated from business logic.
This keeps use-cases testable and easier to evolve.

### 2) Domain errors, HTTP mapping at API boundary

Services raise domain-specific errors.
API handlers map them into HTTP status codes.
This avoids leaking transport concerns into business logic.

### 3) Redis-backed refresh token rotation

Refresh tokens are one-time style with invalidation by `jti`.
This reduces replay risk and gives server-side token control.

### 4) Stripe webhook-driven payment state

Order payment status is finalized from signed webhook events, not client callbacks.
This provides stronger consistency for payment outcomes.

### 5) Containerized local setup

The app, PostgreSQL, and Redis run in one Compose stack to minimize onboarding friction and improve reproducibility.