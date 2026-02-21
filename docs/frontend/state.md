# State Management

Depict AI uses **Vue 3 Composition API composables** for state management. There is no Vuex or Pinia store — each composable encapsulates reactive state and logic for a specific domain.

## Composables

All composables live in `src/frontend/composables/`.

---

### `useApi.ts`

A thin wrapper around Nuxt's `$fetch` that automatically injects the Clerk authentication token into every request.

```typescript
const api = useApi()

// GET with optional query params
const data = await api.get('/projects', { skip: 0, limit: 20 })

// POST
await api.post('/projects', { name: 'My Dataset' })

// PUT
await api.put(`/projects/${id}`, { description: 'Updated' })

// DELETE
await api.delete(`/projects/${id}`)
```

**How auth works:** On every call, `useApi` retrieves a short-lived JWT from `$clerk.session.getToken()` and attaches it as `Authorization: Bearer <token>`.

The base URL is read from `runtimeConfig.public.apiBaseUrl` (defaults to `http://localhost:8000`).

---

### `useAuth.ts`

Wraps Clerk authentication state for use in components and middleware.

Provides:
- Current user information
- Sign-in / sign-out helpers
- Auth-ready reactive flag

---

### `useAnnotationData.ts`

Manages the annotation data lifecycle for the annotation editor page:

- Fetching existing annotations for an image
- Creating new annotations
- Updating / deleting annotations
- Tracking unsaved changes

---

### `useKonvaCanvas.ts`

Controls the **Konva.js** canvas used in the annotation editor.

Responsibilities:
- Canvas initialization and teardown
- Image loading and rendering
- Zoom and pan
- Stage-level event handling (click, drag)
- Coordinate conversion between screen and image space

---

### `useShapeDrawing.ts`

Handles the active drawing interaction for a selected tool:

- Bounding box drawing (click-drag)
- Polygon drawing (click-by-click with close on first-point click)
- Mask / segmentation drawing
- Keypoint placement

---

### `useShapeManagement.ts`

Manages the list of drawn shapes on the canvas:

- Shape selection and deselection
- Shape deletion
- Label assignment to shapes
- Undo/redo stack

---

## Data Flow

```
User action (click / drag)
    │
    ▼
useShapeDrawing  ──►  useShapeManagement  ──►  useAnnotationData
(draw shape)          (add to shape list)       (sync to backend)
                              │
                              ▼
                       useKonvaCanvas
                       (re-render canvas)
```

---

## Environment Variables

Runtime configuration is injected at build time via `nuxt.config.ts`:

| Variable | Description | Default |
|----------|-------------|---------|
| `VITE_CLERK_PUBLISHABLE_KEY` | Clerk authentication public key | — |
| `VITE_API_BASE_URL` | Backend API base URL | `http://localhost:8000` |
