# FastAPI Backend Deployment (Hostinger VPS)

## 1) Install system dependencies
- Python 3.10+
- PostgreSQL client libs
- Nginx

## 2) Setup virtualenv
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 3) Environment variables
Update the project root `.env` file (already created) with correct values for:
- `DATABASE_URL`
- `SECRET_KEY`
- `ALLOWED_HOSTS`

## 4) Run the app
```bash
gunicorn -c gunicorn_conf.py app.main:app
```

## 5) Nginx reverse proxy (example)
```
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /path/to/Employee-Progress-Tracker/backend/static/;
    }

    location /media/ {
        alias /path/to/Employee-Progress-Tracker/backend/media/;
    }
}
```
