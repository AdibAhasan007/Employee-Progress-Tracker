"""
Migration script to add 'url' column to website_usages table if it doesn't exist.
Run this once if you're updating from an older version.
"""
import sqlite3
import config

def add_url_column():
    """
    Safely adds the 'url' column to website_usages table if it doesn't exist.
    """
    try:
        conn = sqlite3.connect(config.DB_PATH)
        cur = conn.cursor()
        
        # Check if url column exists
        cur.execute("PRAGMA table_info(website_usages)")
        columns = [col[1] for col in cur.fetchall()]
        
        if 'url' not in columns:
            print("Adding 'url' column to website_usages table...")
            cur.execute("""
                ALTER TABLE website_usages
                ADD COLUMN url TEXT
            """)
            conn.commit()
            print("✅ Successfully added 'url' column!")
        else:
            print("✅ 'url' column already exists.")
        
        conn.close()
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    add_url_column()
