
# Installation


launch server ( backend ) :
cd src/backend
fastapi dev endpoints.py

launch client ( frontend ) :
cd frontend/nicegui
python3 main.py


# open documentation
mkdocs serve


# launch monitoring tool
Self-host Sentry locally

Sentry can run locally using Docker:

docker run -d --name sentry -p 9000:9000 sentry

Visit http://localhost:9000 to access the Sentry dashboard.

Create a project to get the local DSN (usually http://<host>:9000/<project_id>).
