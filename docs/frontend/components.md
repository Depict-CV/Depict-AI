# Frontend Components

The Depict AI frontend is organized into two main component namespaces: `annot/` for the annotation editor, and `main/` for the dashboard panels.

## Directory Structure

```
src/frontend/components/
├── annot/
│   ├── AIAnnotationButton.vue
│   ├── AnnotationControlsPanel.vue
│   ├── AnnotationEditor.vue
│   ├── AnnotationEditorRefactored.vue
│   ├── AnnotationHistory.vue
│   ├── AnnotationInfoPanel.vue
│   ├── AnnotationToolbar.vue
│   └── ImageAdjustments.vue
└── main/
    ├── AIPanel.vue
    ├── ExportPanel.vue
    ├── FilterPanel.vue
    ├── ImageGallery.vue
    ├── ImportPanel.vue
    ├── ModelAnalysisPanel.vue
    ├── OrganisationPanel.vue
    ├── ProfileMenu.vue
    ├── ProjectSettingsPanel.vue
    ├── ProjectsPanel.vue
    ├── SettingsDialog.vue
    ├── StatsPanel.vue
    └── SubscriptionPanel.vue
```

---

## Main Components

### `ImageGallery.vue`

The central dashboard component that renders a paginated grid of images for a given project.

**Props:**

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `projectId` | `Number` | `null` | ID of the active project |
| `filters` | `Object` | `{}` | Active filter criteria (status, labels, etc.) |
| `inferenceResults` | `Object` | `null` | AI inference output to overlay on images |

**Emits:**

| Event | Description |
|-------|-------------|
| `selectImage` | Fired when the user opens an image for annotation |
| `modifyRequest` | Fired when bulk modification is requested |
| `selectionChange` | Fired when the selection set changes |

**Features:**
- Infinite scroll with batches of 20 images
- Multi-select mode with select-all toggle
- Review mode to accept/reject AI predictions
- Displays annotation status badges per image

---

### `ProjectsPanel.vue`

Lists and manages all projects the user has access to. Lets users create, archive, or delete projects.

---

### `FilterPanel.vue`

Provides filter controls (annotation status, data type, labels) that are passed as props down to `ImageGallery`.

---

### `ImportPanel.vue`

Handles image upload — either via direct upload or by syncing from a MinIO bucket.

---

### `ExportPanel.vue`

Exports annotated datasets in various formats (COCO, YOLO, Pascal VOC).

---

### `AIPanel.vue`

Triggers AI inference jobs on images and displays in-progress status.

---

### `ModelAnalysisPanel.vue`

Displays model performance metrics (precision, recall, confusion matrix) after inference.

---

### `StatsPanel.vue`

Shows dataset statistics: annotation distribution, image counts per status, label frequency.

---

### `ProfileMenu.vue`

Dropdown menu for user account actions: profile, settings, sign out.

---

### `OrganisationPanel.vue`

Manages organisation members and their permission levels.

---

### `ProjectSettingsPanel.vue`

Edit project metadata (name, description) and configure MinIO storage integration.

---

### `SettingsDialog.vue`

Global application settings modal.

---

### `SubscriptionPanel.vue`

Subscription tier and billing management.

---

## Annotation Components

### `AnnotationEditor.vue` / `AnnotationEditorRefactored.vue`

Full-screen canvas editor for annotating images. Powered by **Konva.js** (via `useKonvaCanvas`).  
Supports bounding boxes, polygons, masks, and keypoints.

---

### `AnnotationToolbar.vue`

Tool selection sidebar inside the annotation editor: pointer, bounding box, polygon, mask, keypoint tools.

---

### `AnnotationControlsPanel.vue`

Right-side panel in the annotation editor providing shape list, label assignment, and shape properties.

---

### `AnnotationInfoPanel.vue`

Displays metadata about the currently selected annotation (coordinates, label, status).

---

### `AnnotationHistory.vue`

Shows the annotation revision history for an image, allowing users to revert to previous states.

---

### `AIAnnotationButton.vue`

Trigger button to run AI inference on the currently open image directly from the editor.

---

### `ImageAdjustments.vue`

Controls for brightness, contrast, and saturation adjustments of the canvas image (visual aids only, not stored).
