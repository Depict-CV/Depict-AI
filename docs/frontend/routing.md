# Routing

Depict AI uses **Nuxt 3 file-based routing**. Every file inside `src/frontend/pages/` automatically becomes a route.

## Route Table

| File | Route | Description |
|------|-------|-------------|
| `pages/index.vue` | `/` | Main dashboard (projects + image gallery) |
| `pages/login.vue` | `/login` | Authentication page (Clerk sign-in) |
| `pages/annotate/[id].vue` | `/annotate/:id` | Annotation editor for image with the given ID |

---

## Pages

### `/` — Dashboard (`index.vue`)

The main application page. Requires the user to be authenticated (enforced by the `auth` middleware).

Renders the full dashboard layout:
- Left sidebar with navigation icons
- Side panel (switches between Projects, Filters, Import, Export, AI, Stats, etc.)
- `ImageGallery` in the main area

### `/login` — Login (`login.vue`)

Unauthenticated landing page. Renders the Clerk `<SignIn>` component.  
Redirects to `/` after successful authentication.

### `/annotate/:id` — Annotation Editor (`[id].vue`)

Full-screen annotation editor for a specific image (`id` is the image's database ID).

Loads:
- The image from MinIO / the backend
- Existing annotations via `useAnnotationData`
- Konva canvas via `useKonvaCanvas`

---

## Auth Middleware

`src/frontend/middleware/auth.ts` is a global route middleware that runs on every navigation.

- If the user is **not authenticated**, they are redirected to `/login`.
- The `/login` page itself is excluded from the redirect to avoid loops.

```
Any route
    │
    ▼
auth middleware
    ├── authenticated?  ──► allow navigation
    └── not authenticated?  ──► redirect to /login
```

---

## Navigation

Navigation between pages is handled with Nuxt's `navigateTo()` helper and `<NuxtLink>` components.

Opening an image in the editor:

```vue
<!-- inside ImageGallery.vue -->
navigateTo(`/annotate/${image.id}`)
```

Returning to the dashboard from the editor uses the browser's `history.back()` or a fixed link to `/`.

---

## Nuxt Configuration

Route-level settings are defined in `src/frontend/nuxt.config.ts`:

```typescript
runtimeConfig: {
  public: {
    clerkPublishableKey: process.env.VITE_CLERK_PUBLISHABLE_KEY || '',
    apiBaseUrl: process.env.VITE_API_BASE_URL || 'http://localhost:8000',
  },
},
```
