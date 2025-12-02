# Code Style Guide

This document outlines the coding standards and best practices for Depict AI.

## Python (Backend)

### Style Guide

Follow **PEP 8** with these specifics:

- **Line length:** 120 characters max
- **Indentation:** 4 spaces
- **Quotes:** Double quotes for strings
- **Imports:** Grouped (stdlib, third-party, local)

### Type Hints

Always use type hints for function parameters and return values:

```python
from typing import Optional, List

def get_user(user_id: int) -> Optional[User]:
    """Fetch user by ID."""
    return db.query(User).filter(User.id == user_id).first()

def get_projects(user_id: int, limit: int = 10) -> List[Project]:
    """Get user's projects."""
    return db.query(Project).filter(Project.owner_id == user_id).limit(limit).all()
```

### Docstrings

Use Google-style docstrings:

```python
def create_project(name: str, description: Optional[str] = None) -> Project:
    """Create a new project.
    
    Args:
        name: Project name
        description: Optional project description
        
    Returns:
        Created project instance
        
    Raises:
        ValueError: If name is empty or already exists
    """
    if not name:
        raise ValueError("Project name cannot be empty")
    
    project = Project(name=name, description=description)
    db.add(project)
    db.commit()
    return project
```

### Naming Conventions

```python
# Variables and functions: snake_case
user_count = 10
def calculate_total():
    pass

# Classes: PascalCase
class UserModel:
    pass

# Constants: UPPER_SNAKE_CASE
MAX_UPLOAD_SIZE = 10_000_000
API_VERSION = "v1"

# Private: Leading underscore
def _internal_helper():
    pass
```

### FastAPI Endpoints

```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

router = APIRouter(prefix="/api/v1", tags=["projects"])

@router.post("/projects/", status_code=status.HTTP_201_CREATED)
async def create_project(
    project: ProjectCreate,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
) -> ProjectResponse:
    """
    Create a new project.
    
    Requires authentication.
    """
    # Implementation
    pass
```

### Error Handling

```python
from fastapi import HTTPException, status

# Use appropriate HTTP status codes
if not project:
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Project not found"
    )

# Specific exception types
try:
    result = dangerous_operation()
except ValueError as e:
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=str(e)
    )
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Internal server error"
    )
```

### Async/Await

```python
# Use async for I/O operations
async def fetch_user_data(user_id: int) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.get(f"/users/{user_id}")
        return response.json()

# Sync for CPU-bound operations
def process_image(image_path: str) -> np.ndarray:
    img = Image.open(image_path)
    return np.array(img)
```

### Linting

Use **Ruff** for linting and formatting:

```bash
# Format code
poetry run ruff format .

# Check for issues
poetry run ruff check .

# Fix auto-fixable issues
poetry run ruff check --fix .
```

## JavaScript/Vue (Frontend)

### Style Guide

- **Line length:** 100 characters preferred
- **Indentation:** 2 spaces
- **Quotes:** Single quotes for strings
- **Semicolons:** Optional (consistent usage)

### Vue Component Structure

```vue
<script setup>
import { ref, computed, onMounted } from 'vue';
import { Icon } from 'lucide-vue-next';

// Props
const props = defineProps({
  title: {
    type: String,
    required: true
  },
  items: {
    type: Array,
    default: () => []
  }
});

// Emits
const emit = defineEmits(['select', 'delete']);

// State
const selected = ref(null);
const loading = ref(false);

// Computed
const filteredItems = computed(() => {
  return props.items.filter(item => item.active);
});

// Methods
const handleSelect = (item) => {
  selected.value = item;
  emit('select', item);
};

// Lifecycle
onMounted(() => {
  // Initialization
});
</script>

<template>
  <div class="component-container">
    <h2>{{ title }}</h2>
    <div 
      v-for="item in filteredItems" 
      :key="item.id"
      @click="handleSelect(item)"
    >
      {{ item.name }}
    </div>
  </div>
</template>

<style scoped>
.component-container {
  padding: var(--spacing-md);
}
</style>
```

### Naming Conventions

```javascript
// Variables: camelCase
const userData = {};
const isLoading = false;

// Constants: UPPER_SNAKE_CASE
const MAX_ITEMS = 100;
const API_BASE_URL = 'http://localhost:8000';

// Components: PascalCase (files too)
// LoginPage.vue
// UserProfile.vue

// Props: camelCase
defineProps({
  userId: Number,
  isActive: Boolean
});

// Events: kebab-case
emit('user-selected', user);
emit('item-deleted', id);
```

### Reactive State

```javascript
import { ref, reactive, computed } from 'vue';

// Use ref for primitives
const count = ref(0);
const name = ref('');

// Use reactive for objects
const user = reactive({
  name: '',
  email: '',
  age: 0
});

// Use computed for derived state
const fullName = computed(() => {
  return `${user.firstName} ${user.lastName}`;
});

// Access ref values with .value
count.value++;
console.log(name.value);

// Access reactive props directly
user.name = 'John';
```

### API Calls

```javascript
// Extract to composable functions
const useProjects = () => {
  const projects = ref([]);
  const loading = ref(false);
  const error = ref(null);

  const fetchProjects = async () => {
    loading.value = true;
    error.value = null;
    
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('http://localhost:8000/projects/my-projects', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (!response.ok) {
        throw new Error('Failed to fetch projects');
      }
      
      projects.value = await response.json();
    } catch (err) {
      error.value = err.message;
      console.error('Error fetching projects:', err);
    } finally {
      loading.value = false;
    }
  };

  return { projects, loading, error, fetchProjects };
};
```

### CSS Conventions

```css
/* Use CSS variables */
.button {
  padding: var(--spacing-sm) var(--spacing-md);
  background: var(--color-primary);
  border-radius: var(--radius-md);
}

/* Use BEM-like naming for complex components */
.card {}
.card__header {}
.card__body {}
.card--highlighted {}

/* Keep selectors specific but not too nested */
/* Good */
.sidebar .menu-item {}

/* Avoid */
.sidebar ul li a span {}
```

## Git Commit Messages

### Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

- **feat**: New feature
- **fix**: Bug fix
- **docs**: Documentation
- **style**: Formatting, missing semicolons, etc
- **refactor**: Code restructuring
- **test**: Adding tests
- **chore**: Maintenance

### Examples

```
feat(auth): add GitHub OAuth2 support

Implemented GitHub OAuth2 flow with callback handling
and user creation/linking.

Closes #123

---

fix(projects): prevent duplicate project creation

Added unique constraint check before inserting new project.

---

docs(api): update authentication endpoints

Added examples for all auth endpoints and error responses.

---

refactor(frontend): extract API calls to composables

Created useProjects and useAuth composables for better code organization.
```

## Comments

### Python

```python
# Good: Explain why, not what
# Use binary search because list is sorted and large
result = binary_search(sorted_list, target)

# Bad: Redundant comment
# Increment counter
counter += 1

# Good: Complex logic explanation
# Calculate weighted average considering zero-weight items
# which should be excluded from the denominator
weighted_avg = sum(v * w for v, w in items if w > 0) / sum(w for w in weights if w > 0)
```

### Vue/JavaScript

```javascript
// Good: Explain complex business logic
// Use debounce to prevent excessive API calls while typing
const debouncedSearch = debounce(search, 300);

// Bad: State the obvious
// Set loading to true
loading.value = true;

// Good: Document non-obvious behavior
// OAuth providers return different email field names
const email = user.email || user.mail || user.userPrincipalName;
```

## Tools

### Python

```bash
# Ruff for formatting and linting
poetry run ruff format .
poetry run ruff check .

# pytest for testing
poetry run pytest
poetry run pytest --cov
```

### JavaScript

```bash
# ESLint (if configured)
npm run lint

# Prettier (if configured)
npm run format
```

## Resources

- [PEP 8](https://peps.python.org/pep-0008/)
- [FastAPI Best Practices](https://fastapi.tiangolo.com/tutorial/)
- [Vue.js Style Guide](https://vuejs.org/style-guide/)
- [Conventional Commits](https://www.conventionalcommits.org/)
