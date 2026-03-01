# Frontend Overview

The Depict AI frontend is built with **Vue.js 3** using the Composition API, providing a modern, reactive interface for managing computer vision datasets.

## Architecture

```
src/frontend/
├── app.vue                 # Root app component
├── assets/                 # Static assets and global CSS
├── components/             # Reusable Vue components
├── composables/            # Shared Composition API logic
├── middleware/             # Route middleware
├── pages/                  # File-based routes
├── plugins/                # Nuxt plugins
├── public/                 # Public static files
├── nuxt.config.ts          # Nuxt configuration
└── package.json            # npm scripts and dependencies
```

## Tech Stack

- **Vue.js 3** - Progressive JavaScript framework
- **Composition API** - Modern Vue reactivity
- **Nuxt 3** - Vue framework for routing and app structure
- **Lucide Vue Next** - Icon library
- **Native Fetch API** - HTTP requests
- **localStorage** - Client-side state persistence

## Key Features

### 🎨 UI Components

- **LoginPage** - Authentication with OAuth2 social login
- **Menubar** - Top navigation bar
- **Sidebar** - Main navigation with icon buttons
- **NavPanel** - Side panel container for different views
- **ImageGallery** - Grid display of images
- **ManualAnnotationPage** - Full-screen annotation interface

### 📦 Panels

- **ProjectsPanel** - Create and manage projects
- **UploadPanel** - Upload images to projects
- **FilterPanel** - Filter and search images
- **AiAnnotationPanel** - AI-assisted annotation controls

### 🔐 Authentication

- Local email/password authentication
- OAuth2 social login (Google, Microsoft, GitHub)
- JWT token storage in localStorage
- Auto-redirect on OAuth callback

### 🎯 State Management

- Reactive refs with Composition API
- Local component state
- localStorage for persistence
- No centralized store (simple app)

## Component Structure

### Composition API Pattern

```vue
<script setup>
import { ref, onMounted } from 'vue';

// Reactive state
const data = ref([]);
const loading = ref(false);

// Methods
const fetchData = async () => {
  loading.value = true;
  // Fetch logic
  loading.value = false;
};

// Lifecycle
onMounted(() => {
  fetchData();
});
</script>

<template>
  <div>
    <!-- Template -->
  </div>
</template>

<style scoped>
/* Component styles */
</style>
```

## Styling

### CSS Architecture

- **Scoped styles** - Component-level CSS
- **CSS Variables** - Global design tokens
- **No preprocessor** - Pure CSS
- **Modern features** - Grid, Flexbox, custom properties

### Global CSS Variables

```css
:root {
  /* Colors */
  --color-primary: #667eea;
  --color-secondary: #764ba2;
  --color-bg: #ffffff;
  --color-text: #2c3e50;
  
  /* Spacing */
  --spacing-xs: 4px;
  --spacing-sm: 8px;
  --spacing-md: 16px;
  --spacing-lg: 24px;
  
  /* Border radius */
  --radius-sm: 4px;
  --radius-md: 8px;
  --radius-lg: 16px;
}
```

## API Integration

### Authentication

```javascript
// Login
const response = await fetch('http://localhost:8000/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    username: email,
    hashed_password: hashedPassword
  })
});

const data = await response.json();
localStorage.setItem('token', data.access_token);
```

### Authenticated Requests

```javascript
const token = localStorage.getItem('token');

const response = await fetch('http://localhost:8000/projects/my-projects', {
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  }
});
```

## Running the Frontend

### Development Mode

```bash
cd src/frontend
npm run dev
```

Frontend available at: http://localhost:3000

### Production Build

```bash
cd src/frontend
npm run build
```

Build output in `.output/` directory.

### Preview Production Build

```bash
npm run preview
```

## Environment Configuration

Frontend uses Nuxt runtime config with environment variables:

```javascript
const config = useRuntimeConfig();
const API_URL = config.public.apiBaseUrl;
```

Create `.env` in `src/frontend/`:

```env
VITE_API_BASE_URL=https://api.yourdomain.com
```

## Development Tips

### Hot Module Replacement (HMR)

Nuxt dev server provides instant HMR. Changes reflect immediately without full reload.

### Vue DevTools

Install [Vue DevTools](https://devtools.vuejs.org/) browser extension for debugging:

- Inspect component hierarchy
- View reactive state
- Time-travel debugging
- Performance profiling

### Code Organization

- Keep components small and focused
- Use Composition API for logic reuse
- Scoped styles prevent CSS conflicts
- Props for parent-child communication
- Emits for child-parent communication

## Testing

See [Frontend Testing](../contributing.md) for testing strategies.

```bash
# Run lint checks
npm run lint

# Check formatting
npm run format:check
```

## Next Steps

- [Components Guide](components.md) - Detailed component docs
- [State Management](state.md) - State patterns
- [Routing](routing.md) - Navigation setup
- [Styling Guide](styling.md) - CSS conventions
