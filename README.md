# Confidential Informant Help Desk

Confidential Informant Help Desk is a Flask Progressive Web App built for Docker deployment, Railway hosting, and a PostgreSQL database. It includes mobile-first case intake, encrypted evidence uploads, department coordination, secure messaging, CAD-style reporting, and lawful public-data reference tools.

## Deployment assumptions

- App runtime: Docker container
- Hosting: Railway
- Database: PostgreSQL
- Reverse proxy and TLS: Railway edge
- Mobile install target: Safari on iPhone

## Core capabilities

- Mobile-first dashboard with large app-style navigation for iPhone home screen installation
- Role-based authentication for admin, officer, analyst, and informant users
- Case management with notes, activity history, encrypted attachments, and department associations
- Department directory seeded with Capital District agencies
- CAD-style report generation with PDF export and print view
- Lawful public-data and public-records discovery using official open-data portals and agency links only
- Audit logging for login, case access, attachment downloads, and report generation

## Legal and operational guardrails

- This app only references lawful public APIs, official open-data portals, and agency-controlled public links.
- It does not scrape restricted systems, bypass CAPTCHAs, defeat paywalls, or connect to private law-enforcement systems.
- If a source requires payment, login, or manual verification, the UI links to the official source and stops there.

## Docker local development

1. Copy the environment template.

```powershell
Copy-Item .env.example .env
```

2. Start the app and PostgreSQL.

```powershell
docker compose up --build
```

3. Open the app at http://localhost:8080.

4. On first launch, create the bootstrap administrator at /auth/bootstrap.

The Compose stack provides a Flask web container, a PostgreSQL 16 database, a persistent `app-data` volume for encrypted uploads and exports, and a persistent `postgres-data` volume for the database.

The Flask entrypoint is `wsgi.py`, and the container starts Gunicorn with `wsgi:app`.

## Railway deployment

1. Create a Railway project from this repository.

2. Add a Railway PostgreSQL service.

3. Set these variables on the Railway web service.

```text
FLASK_ENV=production
SECRET_KEY=<long-random-secret>
APP_ENCRYPTION_KEY=<second-long-random-secret>
APP_STORAGE_ROOT=/app/runtime
```

4. Attach a Railway volume mounted at `/app/runtime`.

This is required because encrypted attachments, generated PDFs, and filesystem-backed sessions need persistent writable storage. Without a volume, Railway container storage is ephemeral.

5. Deploy. Railway will build from the included Dockerfile and monitor `/health`.

6. Open the deployed HTTPS URL in Safari on iPhone, then tap Share and Add to Home Screen.

## PostgreSQL notes

- The app requires `DATABASE_URL` at startup. There is no SQLite fallback.
- `DATABASE_URL` must point to PostgreSQL or the app raises a startup error immediately.
- The app reads `DATABASE_URL` from Railway or Docker Compose.
- Railway may provide the value as `postgres://...` or `postgresql://...`.
- The config normalizes either form to `postgresql+psycopg://...` automatically for SQLAlchemy.

## Included deployment files

- `Dockerfile`
- `docker-compose.yml`
- `.dockerignore`
- `railway.json`

## PWA note

The manifest, service worker, and Safari standalone metadata are already included. For production branding on iPhone, replace the placeholder SVG icon with Apple-sized PNG icons.

## Scaling note

Filesystem storage works for Docker and Railway when you attach a persistent volume. If you later need multiple app instances, move attachments and exports to object storage.