# Setup & Quickstart Guide

## Prerequisites

- Python 3.11+
- Node.js 20+
- PostgreSQL or SQLite (default in local dev)

## 1. Backend Setup

```bash
# From repository root
python -m venv .venv
.venv\Scripts\activate   # Windows
# source .venv/bin/activate  # Linux/macOS

pip install -r backend/requirements.txt
```

### Database Initialization & Seed Data

```bash
# Run database migrations
.venv\Scripts\alembic -c alembic.ini upgrade head

# Seed Rani Fashions demo catalogue, customers & orders
.venv\Scripts\python scripts/seed_demo_data.py
```

### Start Backend API Server

```bash
.venv\Scripts\uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```
API Documentation will be available at `http://localhost:8000/docs`.

---

## 2. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Dashboard will be live at `http://localhost:3000`.

---

## 3. Demo Credentials

- **Email**: `demo@reachoutsmb.com`
- **Password**: `password123`
- **Business**: Rani Fashions (Hyderabad)

Or use the **"Use Demo Account"** button on `/login`.
To test live WhatsApp and Instagram sales conversations immediately without Meta credentials, open `http://localhost:3000/dev/simulator`.
