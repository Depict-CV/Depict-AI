# User Management with Clerk Authentication

## 🎯 How It Works

When users sign in with Clerk, they are **automatically created in your local database**. This ensures all your existing relationships (projects, annotations, data) work perfectly.

### Flow Diagram

```
User Signs In with Clerk
         ↓
Clerk Returns JWT Token
         ↓
Frontend Sends Token to FastAPI
         ↓
FastAPI Validates JWT (clerk_auth.py)
         ↓
get_current_clerk_user() checks database:
         ├─ User exists? → Return existing user
         └─ User doesn't exist? → Create new user
                                   ↓
                        User created with:
                        - oauth_provider: "clerk"
                        - oauth_id: Clerk user ID
                        - email: from Clerk
                        - username: from Clerk
                        - hashed_password: NULL
                        - permission: VIEW_ONLY
         ↓
User object returned to endpoint
         ↓
All queries filter by current_user.id
```

## 🗄️ Database Schema

### User Model (Updated)

```python
class User(SQLModel, table=True):
    id: int | None                          # Primary key
    username: str                            # Unique username
    email: str                              # Unique email
    hashed_password: str | None = None      # ✅ Now nullable for OAuth users
    permission: PermissionEnum              # User permission level
    
    # OAuth fields
    oauth_provider: str | None = None       # "clerk", "google", etc.
    oauth_id: str | None = None             # Provider's user ID
    
    # Relationships
    data: List["Data"]                      # User's uploaded data
    projects: List["Project"]               # User's projects (many-to-many)
```

### Key Relationships

**Projects:**
```python
class Project(SQLModel, table=True):
    id: int
    name: str
    owner_id: int  # Foreign key to User.id
    users: List[User]  # Many-to-many relationship
```

**Annotations:**
```python
class Annotation(SQLModel, table=True):
    id: int
    label: str
    author_id: int  # Foreign key to User.id ← Filtered by current user
    project_id: int
    data_id: int
```

**Data:**
```python
class Data(SQLModel, table=True):
    id: int
    type: DataTypeEnum
    author_id: int  # Foreign key to User.id ← Filtered by current user
    project_id: int
```

## 🔐 How Authentication Works

### Backend (FastAPI)

Every protected endpoint uses this dependency:

```python
from src.backend.api.clerk_auth import get_current_clerk_user

@router.get("/projects/my-projects")
def get_user_projects(
    current_user: User = Depends(get_current_clerk_user),
    db: Session = Depends(get_session)
):
    # current_user is automatically:
    # 1. Created in DB if first login
    # 2. Fetched from DB if returning user
    # 3. Has valid id, email, username, etc.
    
    # Now filter by current user
    statement = select(Project).join(ProjectUserLink).where(
        ProjectUserLink.user_id == current_user.id
    )
    projects = db.exec(statement).all()
    return projects
```

### What Happens on First Login

1. User signs in with Clerk (Google, email, etc.)
2. Clerk issues JWT token with:
   - `sub`: Clerk user ID (e.g., "user_abc123")
   - `email`: "user@example.com"
   - `username`: "john_doe"

3. `get_current_clerk_user()` receives token and:
   ```python
   # Check if user exists
   user = db.query(User).filter(
       User.oauth_provider == "clerk",
       User.oauth_id == "user_abc123"
   ).first()
   
   if not user:
       # Create new user
       user = User(
           username="john_doe",
           email="user@example.com",
           hashed_password=None,  # OAuth users don't have passwords
           permission=PermissionEnum.VIEW_ONLY,
           oauth_provider="clerk",
           oauth_id="user_abc123"
       )
       db.add(user)
       db.commit()
   
   return user  # user.id is now available!
   ```

4. Now `user.id` exists and can be used for all relationships:
   - Creating projects: `project.owner_id = current_user.id`
   - Creating annotations: `annotation.author_id = current_user.id`
   - Filtering data: `WHERE author_id = current_user.id`

## 📊 Displaying Targeted Content

### Example 1: Show User's Projects

```python
@router.get("/projects/my-projects")
def get_my_projects(
    current_user: User = Depends(get_current_clerk_user),
    db: Session = Depends(get_session)
):
    # Get projects where user is a member
    statement = (
        select(Project)
        .join(ProjectUserLink)
        .where(ProjectUserLink.user_id == current_user.id)
    )
    projects = db.exec(statement).all()
    return projects
```

### Example 2: Show User's Annotations

```python
@router.get("/annotations/my-annotations")
def get_my_annotations(
    current_user: User = Depends(get_current_clerk_user),
    db: Session = Depends(get_session)
):
    # Get only annotations created by current user
    statement = select(Annotation).where(
        Annotation.author_id == current_user.id
    )
    annotations = db.exec(statement).all()
    return annotations
```

### Example 3: Show User's Data Uploads

```python
@router.get("/data/my-uploads")
def get_my_uploads(
    current_user: User = Depends(get_current_clerk_user),
    db: Session = Depends(get_session)
):
    # Get only data uploaded by current user
    statement = select(Data).where(
        Data.author_id == current_user.id
    )
    data = db.exec(statement).all()
    return data
```

### Example 4: Create Annotation as Current User

```python
@router.post("/annotations/")
def create_annotation(
    annotation_data: AnnotationCreate,
    current_user: User = Depends(get_current_clerk_user),
    db: Session = Depends(get_session)
):
    # Automatically set author_id to current user
    annotation = Annotation(
        label=annotation_data.label,
        status=AnnotationStatus.HUMAN_ANNOTATION,
        author_id=current_user.id,  # ← Automatically set
        data_id=annotation_data.data_id,
        project_id=annotation_data.project_id
    )
    db.add(annotation)
    db.commit()
    return annotation
```

## 🔄 User Sync on Login

The system automatically syncs user data from Clerk:

```python
# If user already exists, update their info
if user:
    if email and user.email != email:
        user.email = email  # Update email if changed
    if username and user.username != username:
        user.username = username  # Update username if changed
    db.commit()
```

This ensures user info stays current even if they change it in Clerk.

## 🚀 Frontend Usage

### Making Authenticated Requests

```javascript
import { useApi } from '@/composables/useApi'

const api = useApi()

// Get current user's projects
const projects = await api.get('/projects/my-projects')

// Create annotation (automatically linked to current user)
const annotation = await api.post('/annotations/', {
  label: 'cat',
  data_id: 123,
  project_id: 456
})

// Get current user's annotations
const myAnnotations = await api.get('/annotations/my-annotations')
```

The `useApi()` composable automatically:
1. Gets JWT token from Clerk
2. Adds `Authorization: Bearer <token>` header
3. Sends request to FastAPI
4. FastAPI extracts user from token
5. Returns user-specific data

## 🎨 Frontend User Context

In Vue components, you can access current user info:

```vue
<script setup>
import { useUser } from '@clerk/vue'

const { user } = useUser()

// user contains:
// - user.id (Clerk ID)
// - user.primaryEmailAddress.emailAddress
// - user.username
// - user.firstName, user.lastName
</script>

<template>
  <div v-if="user">
    <h2>Welcome, {{ user.firstName }}!</h2>
    <p>{{ user.primaryEmailAddress.emailAddress }}</p>
  </div>
</template>
```

## 🔍 Debugging User Issues

### Check if User Exists in Database

```python
# In FastAPI endpoint or Python script
from sqlmodel import Session, select
from src.backend.db.database import engine
from src.backend.db.tables import User

with Session(engine) as session:
    # Find user by Clerk ID
    user = session.exec(
        select(User).where(
            User.oauth_provider == "clerk",
            User.oauth_id == "user_abc123"  # From JWT token
        )
    ).first()
    
    if user:
        print(f"User exists: {user.id}, {user.email}")
    else:
        print("User not found in database")
```

### View All Users

Run the migration script:
```powershell
poetry run python scripts/migrate_oauth.py
```

This shows all existing users and their OAuth status.

## 🔧 Migration from Old Auth

If you have existing users from the old authentication system:

### They Still Work!
- Old users have `hashed_password` set
- Old users have `oauth_provider = NULL`
- They can still log in with the old endpoints (if you keep them)

### Migrate Existing User to Clerk
If an existing user wants to use Clerk:

1. They sign in with Clerk using same email
2. New Clerk user is created (different ID)
3. You need to manually merge accounts (optional):

```python
# Manual account merge script
old_user = db.query(User).filter(User.email == "user@example.com", User.oauth_provider == None).first()
new_user = db.query(User).filter(User.email == "user@example.com", User.oauth_provider == "clerk").first()

# Update all references to old user
db.query(Project).filter(Project.owner_id == old_user.id).update({"owner_id": new_user.id})
db.query(Annotation).filter(Annotation.author_id == old_user.id).update({"author_id": new_user.id})
db.query(Data).filter(Data.author_id == old_user.id).update({"author_id": new_user.id})

# Delete old user
db.delete(old_user)
db.commit()
```

## ✅ Verification Checklist

Run this to verify everything is set up:

```powershell
poetry run python scripts/migrate_oauth.py
```

Check:
- ✅ User model has `oauth_provider` and `oauth_id` fields
- ✅ `hashed_password` is nullable
- ✅ Clerk auth module exists
- ✅ Config has Clerk settings
- ✅ Endpoints use `get_current_clerk_user`

## 🎯 Summary

**Your concern:** "Users authenticated with Clerk don't exist in my SQL database"

**Solution:** They do now!

- ✅ User is automatically created in database on first login
- ✅ User has a valid `id` for foreign key relationships
- ✅ Projects, annotations, and data are linked to user via `author_id`/`owner_id`
- ✅ All queries can filter by `current_user.id`
- ✅ Targeted content works exactly as before

**The magic:**
```python
current_user: User = Depends(get_current_clerk_user)
```

This single line:
1. Validates JWT from Clerk
2. Creates/fetches user from database
3. Returns User object with valid `id`
4. Enables all relationships to work

No manual database inserts needed! 🚀
