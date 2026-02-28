# depictAI

**depictAI** is an open-source image data tool designed to **collect, filter, and export large-scale satellite image datasets** for **computer vision and machine learning tasks**.

It provides a **simple web-based user interface** to build datasets from public Earth observation sources such as Sentinel and Landsat, without writing notebooks or scripts.

depictAI focuses on dataset creation at scale.

---

## ✨ Key Features

* 🛰️ Collect satellite images from multiple open datasets
* 🧭 Simple UI workflow
* 🗺️ Interactive map-based selection
* 🗂️ Export datasets containing **thousands of images** in a few clicks
* 📦 Docker-ready for quick setup
* 🧠 Designed for **computer vision & ML pipelines**

---

## 🚀 Why depictAI?

Compared to Sentinel Hub or Jupyter notebooks:

* ✅ **100% free & open source**
* ✅ Much simpler UI than notebooks
* ✅ Local dataset export (no cloud lock-in)
* ✅ Dataset-oriented (not visualization-oriented)
* ✅ Designed to scale to thousands of images

---

## 🛰️ Supported Data Sources

Currently supported via **Microsoft Planetary Computer**:

* **Sentinel-2**
* **Landsat**

All datasets are accessed through open STAC catalogs.

---

## ⚡ Quick Start

```bash
git clone https://github.com/your-org/depictAI.git
cd depictAI
docker compose up
```

Once running:

* Frontend: `http://localhost:3000`
* Backend API docs: `http://localhost:8000/docs`

---

## 🧱 Architecture Overview

* **Backend**: FastAPI

  * Python-only
  * Internal API (not public)
  * Swagger docs available at `/docs`
  * PostgreSQL for metadata & project storage

* **Frontend**: Vue

  * Map-based UI using Leaflet
  * Dataset-driven workflow

* **Orchestration**: Docker Compose (recommended)

---

## 🧭 User Workflow

Dataset creation follows **4 simple steps**:

1. **Create a project**
2. **Request data** (area, time range, filters)
3. **Select images** (sort & filter by date, tile, cloud cover)
4. **Export dataset**

---

## 📦 Dataset Output

Supported / planned formats:

* GeoTIFF
* PNG / JPG
* STAC catalogs

Each dataset includes:

* Image files
* Metadata (acquisition date, tile, cloud cover, source, etc.)

Data is stored **locally**.

---

## 🤝 Contributing

Contributions are **very welcome**.

* Strict contribution guidelines
* Issues and PRs encouraged
* Please open an issue before major changes

(Contribution guide coming soon.)

---

## 🙌 Credits

* Microsoft Planetary Computer
* STAC ecosystem
* Open satellite data providers

---

## Installation

### Prerequisites

- Python 3.12+
- Poetry
- Node.js & npm
- Docker & Docker Compose (optional, for containerized run)

### Setup

1. **Install Python dependencies:**
   ```bash
   poetry install
   ```

2. **Install frontend dependencies:**
   ```bash
   cd src/frontend
   npm install
   ```

### Using Docker Compose

```bash
# Build and start backend + frontend
docker compose up --build

# Stop containers
docker compose down
```

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API docs: http://localhost:8000/docs

### Manual Commands

**Backend (FastAPI):**
```bash
poetry env activate
cd src/backend
fastapi dev endpoints.py
```

**Frontend (Vue.js):**
```bash
cd src/frontend
npm run dev
```

**Documentation:**
```bash
poetry run mkdocs serve
```
