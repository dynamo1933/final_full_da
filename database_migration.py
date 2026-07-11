#!/usr/bin/env python3
"""
Database Migration Script for Spiritual Progress Tracking
Run this script to add the new stage tracking fields to the existing User table.

Usage:
1. Make sure your Flask app is properly configured
2. Run: python database_migration.py
3. The script will add the new columns to the User table

New Fields Added:
- Rudraksha access permissions (8 Mukhi, 11 Mukhi, 14 Mukhi)
- Stage completion dates for all 6 stages
- Stage start dates for duration tracking
- Devi Mandala access permissions (1, 2, 3) for Devi Padathi/Kamakhya Sadhana
"""

import sys
import os
from flask import Flask
from models import db, User
from datetime import datetime
from sqlalchemy import text

def create_app():
    """Create Flask app for migration"""
    app = Flask(__name__)

    # Configuration from app.py
    app.config['SECRET_KEY'] = 'your-secret-key-here-change-in-production'
    
    # Load env variables dynamically
    from dotenv import load_dotenv
    load_dotenv()
    db_url = os.getenv('DATABASE_URL') or os.getenv('SQLALCHEMY_DATABASE_URI')
    if db_url:
        db_url = db_url.strip().replace("\n", "").replace("\r", "")
    if db_url and db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
    if db_url and db_url.startswith("libsql://"):
        db_url = db_url.replace("libsql://", "sqlite+libsql://", 1)
        
    # Ensure there is a slash before the query parameters for sqlite+libsql
    if db_url and "sqlite+libsql://" in db_url and "?" in db_url:
        parts = db_url.split("?", 1)
        if not parts[0].endswith("/"):
            db_url = f"{parts[0]}/?{parts[1]}"
        
    # Fallback to local SQLite if using sqlite+libsql but the driver is not installed
    if db_url and db_url.startswith("sqlite+libsql://"):
        try:
            import sqlalchemy_libsql
        except ImportError:
            print("⚠️  Warning: 'sqlalchemy-libsql' driver is not installed (expected on Windows Python 3.14).")
            print("   Falling back to local SQLite database for migration.")
            db_url = None
        
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url or 'sqlite:///daiva_anughara.db'
    
    # Configure engine options for Turso
    db_uri = app.config['SQLALCHEMY_DATABASE_URI']
    if db_uri.startswith('sqlite+libsql'):
        auth_token = None
        import urllib.parse as urlparse
        try:
            parsed_url = urlparse.urlparse(db_uri)
            query_params = urlparse.parse_qs(parsed_url.query)
            if 'authToken' in query_params:
                auth_token = query_params['authToken'][0]
                clean_url = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}"
                app.config['SQLALCHEMY_DATABASE_URI'] = clean_url
        except Exception as e:
            print(f"⚠️  Warning: Error parsing Turso URI in migration: {e}")
            
        if not auth_token:
            auth_token = os.getenv('TURSO_AUTH_TOKEN')
            
        app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
            'connect_args': {
                'auth_token': auth_token
            }
        }
    else:
        app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {}
        
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['UPLOAD_FOLDER'] = 'uploads'
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

    db.init_app(app)
    return app

def add_stage_tracking_columns():
    """Add new stage tracking columns to User table"""
    print("🕉️ Starting database migration for spiritual progress tracking...")

    try:
        # Add Rudraksha access permissions
        print("📿 Adding Rudraksha access permission fields...")
        try:
            with db.engine.connect() as conn:
                conn.execute(text("ALTER TABLE user ADD COLUMN rudraksha_8_mukhi_access BOOLEAN DEFAULT 0"))
                conn.commit()
            print("   ✓ rudraksha_8_mukhi_access added")
        except Exception as e:
            print(f"   ⚠️ rudraksha_8_mukhi_access: {e}")

        try:
            with db.engine.connect() as conn:
                conn.execute(text("ALTER TABLE user ADD COLUMN rudraksha_11_mukhi_access BOOLEAN DEFAULT 0"))
                conn.commit()
            print("   ✓ rudraksha_11_mukhi_access added")
        except Exception as e:
            print(f"   ⚠️ rudraksha_11_mukhi_access: {e}")

        try:
            with db.engine.connect() as conn:
                conn.execute(text("ALTER TABLE user ADD COLUMN rudraksha_14_mukhi_access BOOLEAN DEFAULT 0"))
                conn.commit()
            print("   ✓ rudraksha_14_mukhi_access added")
        except Exception as e:
            print(f"   ⚠️ rudraksha_14_mukhi_access: {e}")

        # Add Devi Mandala access permissions (for Devi Padathi - Kamakhya Sadhana)
        print("🌸 Adding Devi Mandala access permission fields (Devi Padathi)...")
        try:
            with db.engine.connect() as conn:
                conn.execute(text("ALTER TABLE \"user\" ADD COLUMN devi_mandala_1_access BOOLEAN DEFAULT TRUE"))
                conn.commit()
            print("   ✓ devi_mandala_1_access added")
        except Exception as e:
            print(f"   ⚠️ devi_mandala_1_access: {e}")

        try:
            with db.engine.connect() as conn:
                conn.execute(text("ALTER TABLE \"user\" ADD COLUMN devi_mandala_2_access BOOLEAN DEFAULT FALSE"))
                conn.commit()
            print("   ✓ devi_mandala_2_access added")
        except Exception as e:
            print(f"   ⚠️ devi_mandala_2_access: {e}")

        try:
            with db.engine.connect() as conn:
                conn.execute(text("ALTER TABLE \"user\" ADD COLUMN devi_mandala_3_access BOOLEAN DEFAULT FALSE"))
                conn.commit()
            print("   ✓ devi_mandala_3_access added")
        except Exception as e:
            print(f"   ⚠️ devi_mandala_3_access: {e}")

        # Add stage completion dates
        print("📅 Adding stage completion date fields...")
        completion_fields = [
            'mandala_1_completed_at',
            'mandala_2_completed_at',
            'mandala_3_completed_at',
            'rudraksha_8_mukhi_completed_at',
            'rudraksha_11_mukhi_completed_at',
            'rudraksha_14_mukhi_completed_at'
        ]

        for field in completion_fields:
            try:
                with db.engine.connect() as conn:
                    conn.execute(text(f"ALTER TABLE user ADD COLUMN {field} DATETIME"))
                    conn.commit()
                print(f"   ✓ {field} added")
            except Exception as e:
                print(f"   ⚠️ {field}: {e}")

        # Add stage start dates
        print("⏱️ Adding stage start date fields...")
        start_fields = [
            'mandala_1_started_at',
            'mandala_2_started_at',
            'mandala_3_started_at',
            'rudraksha_8_mukhi_started_at',
            'rudraksha_11_mukhi_started_at',
            'rudraksha_14_mukhi_started_at'
        ]

        for field in start_fields:
            try:
                with db.engine.connect() as conn:
                    conn.execute(text(f"ALTER TABLE user ADD COLUMN {field} DATETIME"))
                    conn.commit()
                print(f"   ✓ {field} added")
            except Exception as e:
                print(f"   ⚠️ {field}: {e}")

        print("✅ Migration completed!")
        print("\n📊 Migration Results:")
        print("   The script attempted to add new spiritual progress tracking fields.")
        print("   Warnings for existing fields are normal - they indicate the columns already exist.")
        print("\n📋 Expected new fields:")
        print("   - Rudraksha access permissions (5, 11, 14 Mukhi)")
        print("   - Stage completion dates for all 6 stages")
        print("   - Stage start dates for duration tracking")

    except Exception as e:
        print(f"❌ Error during migration: {e}")
        print("This might mean the columns already exist or there's a database issue.")
        return False

    return True

def reset_database_for_testing():
    """Optional: Reset database for testing (WARNING: This will delete all data!)"""
    print("⚠️ WARNING: This will delete all existing data!")
    response = input("Are you sure you want to reset the database? (type 'YES' to confirm): ")

    if response == 'YES':
        print("🗑️ Dropping all tables...")
        db.drop_all()
        print("🆕 Creating all tables...")
        db.create_all()
        print("✅ Database reset complete!")
        return True
    else:
        print("❌ Database reset cancelled.")
        return False

if __name__ == "__main__":
    app = create_app()

    with app.app_context():
        print("🕉️ Daiva Anughara - Spiritual Progress Database Migration")
        print("=" * 60)

        if len(sys.argv) > 1 and sys.argv[1] == '--reset':
            reset_database_for_testing()
        else:
            success = add_stage_tracking_columns()

            if success:
                print("\n🎉 Migration completed! The spiritual progress tracking system is ready.")
                print("\nNext steps:")
                print("1. Restart your Flask application")
                print("2. Test the new admin stage management features")
                print("3. Test the user progress bar on the padati page")
                print("4. Update existing users' stage access as needed")
            else:
                print("\n⚠️ Migration failed. Please check the error messages above.")
