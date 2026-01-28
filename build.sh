#!/usr/bin/env bash
# exit on error
set -o errexit

# Navigate to backend directory
cd backend

pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate

# Create admin user automatically during deployment
echo "Creating default admin user..."
python manage.py create_default_admin
