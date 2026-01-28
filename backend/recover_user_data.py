"""
Automated User Data Recovery Script
আপনার local SQLite database থেকে সরাসরি user create করুন
"""
import os
import sys
import django
import sqlite3

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tracker_backend.settings')
django.setup()

from core.models import User

def migrate_users_from_backup():
    """
    Migrate users from data_backup.json or directly from SQLite
    """
    print("🔄 Starting User Data Recovery...\n")
    
    # Option 1: Try to load from data_backup.json
    if os.path.exists('data_backup.json'):
        print("✅ Found data_backup.json - Importing...")
        from django.core.management import call_command
        try:
            call_command('loaddata', 'data_backup.json', verbosity=2)
            print("\n✅ Data imported successfully!")
            return
        except Exception as e:
            print(f"⚠️ Error with loaddata: {e}")
            print("Trying alternate method...\n")
    
    # Option 2: Manual import from local backup
    local_db_path = os.path.expanduser('~') + '/Employee Progress Tracker/hrsoftbdTracker.db'
    if os.path.exists(local_db_path):
        print(f"📂 Found local database: {local_db_path}")
        import_from_local_db(local_db_path)
    else:
        print("❌ No backup files found!")
        print("\nPlease run this command from backend folder:")
        print("  python export_data.py")

def import_from_local_db(db_path):
    """
    Extract users from local SQLite database
    """
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get users from local database
        cursor.execute("""
            SELECT id, username, email, first_name, last_name, password, 
                   role, is_active, is_staff, is_superuser, company_name, designation
            FROM auth_user
        """)
        
        users = cursor.fetchall()
        
        if not users:
            print("❌ No users found in local database!")
            conn.close()
            return
        
        print(f"\n📋 Found {len(users)} users in local database\n")
        
        # Import users
        imported = 0
        for user_data in users:
            uid, username, email, first_name, last_name, password, role, is_active, is_staff, is_superuser, company_name, designation = user_data
            
            # Check if user already exists
            if User.objects.filter(username=username).exists():
                print(f"⏭️  Skipping {username} (already exists)")
                continue
            
            try:
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password[:50] if password else 'default123',  # Use partial hash
                    first_name=first_name or '',
                    last_name=last_name or '',
                    role=role or 'EMPLOYEE',
                    is_active=is_active,
                    company_name=company_name or '',
                    designation=designation or ''
                )
                if is_superuser:
                    user.is_superuser = True
                if is_staff:
                    user.is_staff = True
                user.save()
                
                print(f"✅ Imported: {username} ({role}) - {email}")
                imported += 1
            except Exception as e:
                print(f"❌ Failed to import {username}: {e}")
        
        conn.close()
        print(f"\n✅ Successfully imported {imported} users!")
        
    except Exception as e:
        print(f"❌ Error reading local database: {e}")

def create_demo_user():
    """
    Create a demo user for testing
    """
    if User.objects.filter(username='demo').exists():
        print("Demo user already exists!")
        return
    
    user = User.objects.create_user(
        username='demo',
        email='demo@example.com',
        password='demo123',
        first_name='Demo',
        last_name='User',
        role='EMPLOYEE'
    )
    print(f"✅ Created demo user: demo@example.com / demo123")

if __name__ == '__main__':
    if '--demo' in sys.argv:
        create_demo_user()
    else:
        migrate_users_from_backup()
