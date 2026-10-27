# AfriLearn AI

AfriLearn AI is a child-friendly learning experience for children across Africa and beyond. It combines a colourful learning dashboard, subject paths, interactive mini-games, African-language discovery and a structured lesson builder powered by a Django API.

## Stack
- Django and Python backend
- HTML, CSS and vanilla JavaScript frontend
- PostgreSQL through `DATABASE_URL` when configured; SQLite for local development
- WhiteNoise for static files and Gunicorn for production
- Optional OpenAI-compatible Chat Completions integration, called only from the server

## Run locally
1. Use Python 3.12 or newer.
2. Create and activate a virtual environment.
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Apply migrations:
   ```bash
   python manage.py migrate
   ```
5. Start the development server:
   ```bash
   python manage.py runserver
   ```
6. Open `http://127.0.0.1:8000/`.

## Deploy to Render
The repository includes `render.yaml`. Connect the repository in Render and deploy branch `afrilearn-ai`. For a persistent production database, set `DATABASE_URL` to the Render PostgreSQL internal URL. Set `DJANGO_SECRET_KEY` to a strong secret, `DEBUG=0`, and `ALLOWED_HOSTS=.onrender.com`.

## Turn on AI-generated lessons
The learning API works without a provider key using a guided lesson fallback. To enable AI-generated lessons, add `OPENAI_API_KEY` as a server environment variable in Render. Optionally set `OPENAI_MODEL` to a compatible chat model supported by your API account. Never put provider keys in frontend JavaScript or commit them to Git.

## Current scope
The public learning experience and lesson API are implemented. The parent-owned child-profile and learning-progress models are included as backend foundations, but full family registration, guardian-consent workflow, child account dashboards, and production-grade persisted progress UI remain follow-on work. The anonymous lesson endpoint rate-limits requests and does not persist submitted prompts. AI output can be incorrect; children should check important facts with a trusted adult or teacher.

## Important before public launch
- Connect a persistent PostgreSQL database and confirm automatic backups/retention.
- Configure the production AI provider key and cost/rate limits if AI-generated lessons are wanted.
- Complete parent sign-up, guardian consent, child profile UI and permission tests.
- Test child-safety behavior and accessibility with caregivers and educators.
- Run `python manage.py check --deploy` after configuring production environment variables.
