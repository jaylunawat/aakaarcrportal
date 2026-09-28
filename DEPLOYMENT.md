# Aakaar CR deployment guide

This repository contains two deployment targets:

- `docs/`: privacy-safe, static GitHub Pages preview.
- The Django project: complete portal with accounts, admin, tasks, submissions, password reset, and leaderboard.

## 1. GitHub Pages design preview

Regenerate the preview whenever the templates or static assets change:

```bash
python deploy/export_github_pages.py
```

Then push the repository to GitHub. In **Settings → Pages**, choose **Deploy from a branch**, select the main branch, and choose `/docs` as the publishing folder.

The static build intentionally disables forms and omits live leaderboard records, user accounts, uploaded submissions, and the SQLite database. GitHub Pages supports a branch root or `/docs` as a publishing source: <https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site>

## 2A. Complete portal on Render

`render.yaml` describes a Django web service and PostgreSQL database. Connect the GitHub repository as a new Blueprint in Render. The service will:

- install `requirements-prod.txt`;
- collect static assets;
- run database migrations;
- start Gunicorn;
- expose `/healthz` for health checks.

During Blueprint creation, Render asks for the three administrator variables marked `sync: false`. Enter a private username, email, and strong password. The first deployment creates that administrator automatically; the password is never stored in GitHub.

The free demo uses the console email backend because free Render services cannot connect to common SMTP ports. Password-reset email delivery therefore remains disabled in the free demo.

On a paid Render service with Shell access, an additional administrator can also be created with:

```bash
python manage.py createsuperuser
```

Render's Django guide: <https://render.com/docs/deploy-django>

Important: Render services use an ephemeral filesystem by default. User-uploaded files require object storage or a paid persistent disk mounted at a path supplied through `DJANGO_MEDIA_ROOT`. Render disk documentation: <https://render.com/docs/disks>

## 2B. Complete portal on a VPS with Docker

This option keeps PostgreSQL data and uploaded media in persistent Docker volumes.

1. Copy `.env.example` to `.env`.
2. Set secure values for `DJANGO_SECRET_KEY` and `POSTGRES_PASSWORD`.
3. Set the public domain in `DJANGO_ALLOWED_HOSTS` and its HTTPS origin in `DJANGO_CSRF_TRUSTED_ORIGINS`.
4. Set the SMTP credentials for password reset.
5. Start the stack:

```bash
docker compose up -d --build
docker compose exec web python manage.py createsuperuser
```

The portal listens on port `8000`. Place the VPS reverse proxy in front of it and enable HTTPS.

## Security before the first push

- Never commit `.env`, `db.sqlite3`, `media/`, backups, or the local virtual environment.
- Rotate the previously embedded email password and Django secret before deployment.
- Review `git status` before every push.
- Keep production backups of PostgreSQL and uploaded media.
