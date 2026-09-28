# Aakaar College Representative Portal

The repository is ready for two kinds of publishing:

- **GitHub Pages preview:** the generated `docs/` folder shows the public design on phones and computers. It intentionally contains no accounts, submissions, uploaded files, database, or live leaderboard records.
- **Complete Django portal:** deploy the project through Render or Docker to keep login, registration, password reset, tasks, submissions, leaderboard, and admin features working.

## Preview locally

Run the Django site:

```bash
python manage.py runserver
```

Regenerate and preview the GitHub Pages version:

```bash
python deploy/export_github_pages.py
python -m http.server 8765 --directory docs
```

Then visit <http://127.0.0.1:8765/>.

## Publish

Follow [DEPLOYMENT.md](DEPLOYMENT.md) for the GitHub Pages, Render, and Docker instructions.

Before the first public push, create a `.env` file from `.env.example`, use new credentials, and confirm that the ignored local database, uploads, backups, and virtual environment do not appear in `git status`.
