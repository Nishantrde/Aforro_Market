#!/usr/bin/env bash
# Exit on error
set -o errexit

echo "Building frontend with Vite..."
npm install
npm run build

echo "Running Django collectstatic..."
python manage.py collectstatic --noinput