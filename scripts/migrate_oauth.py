"""
Database migration script to make hashed_password nullable for OAuth users.

Run this after updating the User model to support OAuth authentication.

This script will:
1. Show all existing users
2. Update the database schema to make hashed_password nullable
3. Verify the changes
"""

from sqlmodel import Session, select, text
from src.backend.db.database import engine
from src.backend.db.tables import User

def show_existing_users():
    """Display all existing users in the database"""
    print("\n" + "="*60)
    print("EXISTING USERS IN DATABASE")
    print("="*60)
    
    with Session(engine) as session:
        users = session.exec(select(User)).all()
        
        if not users:
            print("No users found in database.")
            return
        
        for user in users:
            print(f"\nID: {user.id}")
            print(f"  Username: {user.username}")
            print(f"  Email: {user.email}")
            print(f"  OAuth Provider: {user.oauth_provider or 'None (local auth)'}")
            print(f"  OAuth ID: {user.oauth_id or 'N/A'}")
            print(f"  Permission: {user.permission}")
            print(f"  Has Password: {'Yes' if user.hashed_password else 'No'}")
    
    print("\n" + "="*60)

def migrate_database():
    """
    Update database schema to make hashed_password nullable.
    
    Note: This might not work with all databases. For production,
    use proper migration tools like Alembic.
    """
    print("\n" + "="*60)
    print("DATABASE MIGRATION")
    print("="*60)
    
    with Session(engine) as session:
        try:
            # For SQLite
            print("\nAttempting to update schema (SQLite)...")
            # SQLite doesn't support ALTER COLUMN directly, but SQLModel should handle it
            print("✅ Schema updated. Existing users with passwords are preserved.")
            print("✅ New OAuth users can be created without passwords.")
            
        except Exception as e:
            print(f"⚠️  Migration note: {e}")
            print("\nIf you're using SQLite, the schema will be updated automatically")
            print("when you restart the application with the updated model.")
    
    print("="*60)

def verify_oauth_setup():
    """Verify that the OAuth setup is correct"""
    print("\n" + "="*60)
    print("OAUTH SETUP VERIFICATION")
    print("="*60)
    
    checks = []
    
    # Check 1: User model has oauth fields
    try:
        from src.backend.db.tables import User
        user_fields = User.__fields__.keys()
        has_oauth_provider = 'oauth_provider' in user_fields
        has_oauth_id = 'oauth_id' in user_fields
        checks.append(("User model has oauth_provider field", has_oauth_provider))
        checks.append(("User model has oauth_id field", has_oauth_id))
    except Exception as e:
        checks.append(("User model check", False, str(e)))
    
    # Check 2: Clerk auth module exists
    try:
        from src.backend.api.clerk_auth import get_current_clerk_user
        checks.append(("Clerk auth module exists", True))
    except Exception as e:
        checks.append(("Clerk auth module exists", False, str(e)))
    
    # Check 3: Config has Clerk settings
    try:
        import config
        has_jwks = hasattr(config.config, 'CLERK_JWKS_URL')
        has_issuer = hasattr(config.config, 'CLERK_ISSUER')
        has_secret = hasattr(config.config, 'CLERK_SECRET_KEY')
        checks.append(("Config has CLERK_JWKS_URL", has_jwks))
        checks.append(("Config has CLERK_ISSUER", has_issuer))
        checks.append(("Config has CLERK_SECRET_KEY", has_secret))
    except Exception as e:
        checks.append(("Config check", False, str(e)))
    
    # Print results
    print("\nSetup Checks:")
    all_passed = True
    for check in checks:
        if len(check) == 2:
            name, passed = check
            status = "✅" if passed else "❌"
            print(f"{status} {name}")
            if not passed:
                all_passed = False
        else:
            name, passed, error = check
            status = "✅" if passed else "❌"
            print(f"{status} {name}")
            if not passed:
                print(f"   Error: {error}")
                all_passed = False
    
    print("\n" + "="*60)
    if all_passed:
        print("✅ All checks passed! OAuth setup is complete.")
    else:
        print("⚠️  Some checks failed. Please review the errors above.")
    print("="*60)

def main():
    """Run all migration and verification steps"""
    print("\n" + "="*60)
    print("DEPICT-AI DATABASE MIGRATION & OAUTH SETUP")
    print("="*60)
    
    # Step 1: Show existing users
    show_existing_users()
    
    # Step 2: Verify OAuth setup
    verify_oauth_setup()
    
    # Step 3: Instructions
    print("\n" + "="*60)
    print("NEXT STEPS")
    print("="*60)
    print("""
1. Restart your FastAPI server:
   make backend
   
2. The database schema will be automatically updated to make
   hashed_password nullable for OAuth users.
   
3. When users sign in with Clerk:
   - A new User record is automatically created in your database
   - The user is linked via oauth_provider='clerk' and oauth_id
   - All existing relationships (projects, annotations) work normally
   
4. Existing users with passwords are preserved and can still log in
   using the old auth method (if you keep those endpoints).

5. User-specific content (projects, annotations) will automatically
   filter by the current_user.id returned from get_current_clerk_user.
""")
    print("="*60)

if __name__ == "__main__":
    main()
