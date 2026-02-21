# Styling

Depict AI uses **Tailwind CSS** for all styling, configured via `src/frontend/tailwind.config.js`.

## Setup

Tailwind is integrated as a **Nuxt module** (`@nuxtjs/tailwindcss`) and loaded globally via `src/frontend/assets/css/main.css`.

```typescript
// nuxt.config.ts
modules: ['@nuxtjs/tailwindcss'],
css: ['~/assets/css/main.css'],
```

---

## Tailwind Configuration

```javascript
// tailwind.config.js
export default {
  content: [
    './components/**/*.{js,vue,ts}',
    './layouts/**/*.vue',
    './pages/**/*.vue',
    './plugins/**/*.{js,ts}',
    './app.vue',
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          light: '#3b82f6',   // blue-500
          DEFAULT: '#2563eb', // blue-600
          dark: '#1d4ed8',    // blue-700
        },
      },
    },
  },
}
```

### Custom Colors

| Token | Hex | Usage |
|-------|-----|-------|
| `primary-light` | `#3b82f6` | Hover states, secondary buttons |
| `primary` | `#2563eb` | Primary buttons, active states, links |
| `primary-dark` | `#1d4ed8` | Pressed state, focus rings |

---

## Conventions

- **Utility-first:** all styles are applied directly with Tailwind utility classes in the `class` attribute of Vue templates.
- **No scoped CSS unless necessary:** avoid `<style scoped>` blocks; keep all styling in the template.
- **Dark mode:** not yet implemented; reserved for a future iteration.
- **Responsive design:** use Tailwind's responsive prefixes (`sm:`, `md:`, `lg:`) for breakpoint-specific layouts.

---

## Global Styles

`src/frontend/assets/css/main.css` contains:
- Tailwind base/component/utility directives (`@tailwind base`, etc.)
- Any global CSS resets or custom base styles

---

## Icons

The project uses **Lucide Vue Next** for icons:

```vue
<script setup>
import { Trash2, Edit, Check } from 'lucide-vue-next'
</script>

<template>
  <Trash2 class="w-4 h-4 text-red-500" />
</template>
```

Icon sizing and color are controlled with standard Tailwind utilities (`w-*`, `h-*`, `text-*`).
