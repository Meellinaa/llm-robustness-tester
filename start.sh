#!/bin/bash
set -e

cd "$(dirname "$0")/backend"

if [ ! -f .env ]; then
  echo "⚠️  No .env file found. Copying from .env.example..."
  cp .env.example .env
  echo "👉  Edit backend/.env and add your ANTHROPIC_API_KEY, then rerun."
  exit 1
fi

if [ ! -d venv ]; then
  echo "📦  Creating virtualenv..."
  python3 -m venv venv
fi

source venv/bin/activate
pip install -q -r requirements.txt

echo "🚀  Starting backend on http://localhost:8000"
uvicorn main:app --reload --port 8000
