
![Tests](https://github.com/Depict-CV/Depict-AI/actions/workflows/coverage.yml/badge.svg?branch=main)
[![Codecov](https://codecov.io/gh/Depict-CV/Depict-AI/branch/main/graph/badge.svg)](https://codecov.io/gh/Depict-CV/Depict-AI)
[![Stable Documentation](https://img.shields.io/badge/docs-stable-blue.svg)](https://depict-cv.github.io/Depict-AI/)
[![Docs workflow Status](https://github.com/Depict-CV/Depict-AI/actions/workflows/Docs.yml/badge.svg?branch=main)](https://github.com/Depict-CV/Depict-AI/actions/workflows/Docs.yml?query=branch%3Amain)
[![Lint workflow Status](https://github.com/Depict-CV/Depict-AI/actions/workflows/Lint.yml/badge.svg?branch=main)](https://github.com/Depict-CV/Depict-AI/actions/workflows/Lint.yml?query=branch%3Amain)

# Installation


launch server ( backend ) :
```
cd src/backend
fastapi dev endpoints.py
```

launch client ( frontend ) :
```
cd frontend/nicegui
python3 main.py
```


# open documentation
```
mkdocs serve
```


# launch monitoring tool
Self-host Sentry locally

Sentry can run locally using Docker:
```
docker run -d --name sentry -p 9000:9000 sentry
```

Visit http://localhost:9000 to access the Sentry dashboard.

Create a project to get the local DSN (usually http://<host>:9000/<project_id>).
