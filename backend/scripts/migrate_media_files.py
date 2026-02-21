"""
List all media files for manual upload
Since Render free tier doesn't support persistent media storage,
you'll need to use a cloud storage service like AWS S3 or Cloudinary
"""
import os
from pathlib import Path

def list_media_files():
    """List all media files that need to be uploaded"""
    media_root = Path(__file__).parent / 'media'
    
    if not media_root.exists():
        print("❌ Media folder not found!")
        return
    
    print("📁 Media Files to Upload:\n")
    
    file_count = 0
    total_size = 0
    
    for root, dirs, files in os.walk(media_root):
        for file in files:
            file_path = Path(root) / file
            file_size = file_path.stat().st_size
            rel_path = file_path.relative_to(media_root)
            
            file_count += 1
            total_size += file_size
            
            print(f"  {rel_path} ({file_size / 1024:.1f} KB)")
    
    print(f"\n📊 Total: {file_count} files, {total_size / (1024*1024):.2f} MB")
    print("\n⚠️  Important:")
    print("Render free tier does NOT support persistent file storage.")
    print("Media files will be lost when the server restarts.")
    print("\n💡 Solutions:")
    print("1. Use AWS S3 (Recommended)")
    print("2. Use Cloudinary (Free tier available)")
    print("3. Use any cloud storage service")

if __name__ == '__main__':
    list_media_files()
