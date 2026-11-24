# GitHub Pages + FastAPI + Neon

The public page is hosted at https://crimsun-dev.github.io/LIVE-DEMO/.
GitHub Pages serves HTML and JavaScript. FastAPI runs separately and connects to
the existing Neon database using a server-only DATABASE_URL. No database password
or API key belongs in Pages, repository variables, or the public repository.

## Backend

For Render, import this repository as a Blueprint using render.yaml. Set its
DATABASE_URL to the existing Neon **demo** branch URL from backend/.env. Do not
use the test branch. Render generates a DEMO_API_KEY; retrieve it from the service
environment and enter it in the page's API key field when demonstrating writes.
The CORS origin is https://crimsun-dev.github.io (no repository path).

For another Python host: install backend/requirements.txt, work from backend/,
and start `uvicorn app.main:app --host 0.0.0.0 --port $PORT`.
Set DATABASE_URL, DEMO_API_KEY, CORS_ORIGINS, WEATHER_MODE=live and AUTO_SEED=1.
The application creates missing tables and seeds an empty wardrobe on startup.
Existing garments are retained. Do not run measure.py against the demo database:
its database measurement mode resets data.

## Connect Pages

1. Verify the backend's /api/v1/health and /api/v1/wardrobe endpoints return 200.
   Health must report `db: neon`.
2. Set GitHub repository Actions variable API_BASE_URL to the HTTPS backend origin.
3. Run the Deploy GitHub Pages workflow. Only index.html, config.js and .nojekyll
   are uploaded; the backend and .env are excluded.
4. Open Pages, verify wardrobe loading, enter the generated demo API key, then
   test recommendation, save, garment activation and the weather fallback.

You can also enter a backend URL directly in the page's API base field, or pass
`?api=https://your-api-host` while testing. The query parameter takes precedence.
Without a configured backend the page displays a setup message.

This remains the existing synthetic single-user demo. Anyone given its write key
can use the demo controls, including reset. It is not a multi-user wardrobe service.
