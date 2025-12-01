
# Installation

1. activate the poetry env

`poetry env list          # show available virtual environments`

`poetry env activate <path-to-env>`

launch server ( backend ) :

`cd src/backend`

`fastapi dev endpoints.py`

launch client ( frontend nicegui ) :

`cd frontend/nicegui`

`python3 main.py`


launch client ( frontend vue ) :

`cd src/frontend_vue`

`npm run dev`

# open documentation
cd docs
mkdocs serve


# launch monitoring tool
Self-host Sentry locally

Sentry can run locally using Docker:

docker run -d --name sentry -p 9000:9000 sentry

Visit http://localhost:9000 to access the Sentry dashboard.

Create a project to get the local DSN (usually http://<host>:9000/<project_id>).
