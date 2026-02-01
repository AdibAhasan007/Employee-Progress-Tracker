"""
Clean old single-tenant data before multi-tenant migration.
This script deletes all existing data to start fresh with multi-tenant structure.
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tracker_backend.settings')
django.setup()

from core.models import (
    User, WorkSession, Screenshot, ApplicationUsage, 
    WebsiteUsage, ActivityLog, Task,
    CompanySettings
)

def clean_old_data():
    """Delete all old data that doesn't have company FK"""
    print("🧹 Cleaning old single-tenant data...")
    
    # Count before deletion
    counts = {
        'Users (non-OWNER)': User.objects.exclude(role='OWNER').count(),
        'WorkSessions': WorkSession.objects.count(),
        'Screenshots': Screenshot.objects.count(),
        'ApplicationUsage': ApplicationUsage.objects.count(),
        'WebsiteUsage': WebsiteUsage.objects.count(),
        'ActivityLog': ActivityLog.objects.count(),
        'Tasks': Task.objects.count(),
    }
    
    print("\n📊 Current data counts:")
    for model, count in counts.items():
        print(f"  {model}: {count}")
    
    total = sum(counts.values())
    if total == 0:
        print("\n✅ No old data found. Database is clean!")
        return
    
    print(f"\n⚠️  Total records to delete: {total}")
    confirm = input("\n❓ Type 'YES' to confirm deletion: ")
    
    if confirm != 'YES':
        print("❌ Deletion cancelled.")
        return
    
    # Delete in correct order (respect FK constraints)
    print("\n🗑️  Deleting data...")
    
    Screenshot.objects.all().delete()
    print("  ✓ Screenshots deleted")
    
    ApplicationUsage.objects.all().delete()
    print("  ✓ ApplicationUsage deleted")
    
    WebsiteUsage.objects.all().delete()
    print("  ✓ WebsiteUsage deleted")
    
    ActivityLog.objects.all().delete()
    print("  ✓ ActivityLog deleted")
    
    Task.objects.all().delete()
    print("  ✓ Tasks deleted")
    
    WorkSession.objects.all().delete()
    print("  ✓ WorkSessions deleted")
    
    User.objects.exclude(role='OWNER').delete()
    print("  ✓ Non-OWNER users deleted")
    
    CompanySettings.objects.all().delete()
    print("  ✓ CompanySettings deleted")
    
    print("\n✅ Old data cleaned successfully!")
    print("📌 OWNER accounts preserved")
    print("🚀 Ready for multi-tenant migration")

if __name__ == '__main__':
    clean_old_data()
