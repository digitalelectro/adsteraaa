#!/usr/bin/env bash
# Simple launcher for the Streamlit app.
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd -- "${SCRIPT_DIR}/.." && pwd)"

# Load .env if present so PROJECT_ID/LOCATION/GOOGLE_APPLICATION_CREDENTIALS are available.
if [ -f "${PROJECT_ROOT}/.env" ]; then
  set -a
  source "${PROJECT_ROOT}/.env"
  set +a
fi

cd "${PROJECT_ROOT}"

# Create venv if missing
if [ ! -d "${PROJECT_ROOT}/.venv" ]; then
  python3 -m venv .venv
fi

# Activate venv
source "${PROJECT_ROOT}/.venv/bin/activate"

# Install requirements (safe to re-run)
pip install --upgrade pip
pip install -r requirements.txt

# Run Streamlit
exec streamlit run app.py
