"""
Import data from JSON to PostgreSQL database on Render
Run this script from Render Shell after deployment
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tracker_backend.settings')
django.setup()

from django.core.management import call_command

def import_data():
    """Import data from JSON to PostgreSQL"""
    print("📥 Importing data to PostgreSQL database...")
    
    if not os.path.exists('data_backup.json'):
        print("❌ Error: data_backup.json file not found!")
        print("Please ensure the file is in the same directory.")
        return
    
    try:
        # Load data
        call_command('loaddata', 'data_backup.json', verbosity=2)
        print("\n✅ Data imported successfully!")
        
    except Exception as e:
        print(f"\n❌ Error importing data: {e}")
        print("\nTroubleshooting tips:")
        print("1. Ensure migrations are run: python manage.py migrate")
        print("2. Check if data_backup.json is valid JSON")
        print("3. Try importing specific apps one by one")

if __name__ == '__main__':
    import_data()
