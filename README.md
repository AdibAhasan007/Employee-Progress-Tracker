# Employee Progress Tracker

Django-based employee activity tracking system with time tracking, screenshot capture, and task management.

## 🚀 Live Demo
[Deploy to Render](https://render.com)

## 📋 Features
- ✅ Employee time tracking
- ✅ Screenshot capture
- ✅ Application & website usage monitoring
- ✅ Task management
- ✅ Daily/Monthly reports
- ✅ Admin dashboard
- ✅ Company branding customization

## 🛠️ Tech Stack
- **Backend**: Django 4.2+ / Django REST Framework
- **Database**: SQLite (local) / PostgreSQL (production)
- **Storage**: Local / AWS S3 / Cloudinary
- **Server**: Gunicorn + WhiteNoise

## 📦 Installation

### Local Development

```bash
cd backend
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

## 🌐 Deployment to Render

See detailed guide: [RENDER_DEPLOYMENT_GUIDE_BANGLA.md](RENDER_DEPLOYMENT_GUIDE_BANGLA.md)

### Quick Deploy

1. Push to GitHub
2. Connect to Render
3. Set environment variables
4. Deploy!

## 📚 Documentation

- [Render Deployment Guide (Bangla)](RENDER_DEPLOYMENT_GUIDE_BANGLA.md)
- [Data Migration Guide (Bangla)](DATA_MIGRATION_GUIDE_BANGLA.md)
- [Database Backup Summary](DATABASE_BACKUP_SUMMARY.md)

## 🔑 Environment Variables

```env
DEBUG=False
SECRET_KEY=your-secret-key-here
DATABASE_URL=postgresql://...
ALLOWED_HOSTS=your-domain.onrender.com
```

## 📄 License

Proprietary - All rights reserved

## 👨‍💻 Support

For issues and questions, check the documentation files.
