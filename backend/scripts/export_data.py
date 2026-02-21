"""
Export data from SQLite database to JSON format
Run this script before deploying to Render
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tracker_backend.settings')
django.setup()

from django.core.management import call_command

def export_data():
    """Export all data from SQLite to JSON"""
    print("📦 Exporting data from SQLite database...")
    
    # Export all data
    with open('data_backup.json', 'w', encoding='utf-8') as f:
        call_command('dumpdata', 
                    '--natural-foreign',
                    '--natural-primary',
                    '--indent', '2',
                    '--exclude', 'contenttypes',
                    '--exclude', 'auth.permission',
                    '--exclude', 'admin.logentry',
                    '--exclude', 'sessions.session',
                    stdout=f)
    
    print("✅ Data exported successfully to 'data_backup.json'")
    print("\n📋 Next steps:")
    print("1. Upload this file to your GitHub repository")
    print("2. After deploying to Render, run import_data.py script from Render Shell")

if __name__ == '__main__':
    export_data()
