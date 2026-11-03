# TrayCycle

> By team TriCycle (Ian Xie, Gordon Ji, Aryan Mahajan), for 2026-2027 SAS CSHS Hackathon.

A camera-based food-waste tracker for the SAS cafeteria, presented measured waste in kg per dish plus a dashboard the kitchen can act on.

Live site: [traycycle.org](https://traycycle.org)

## Tech stack

### Frontend

- React — Framework
- MUI — UI library
- Vite — Build tool + dev server
- Axios — Handles API requests
- React Router — Client-side routing

### Backend

- Django — Base framework
- Django Rest Framework — RESTful APIs, viewsets, and serializers
- uv — Python dependencies management
- django-filter — Create dynamic filter rules in URL query parameters

### Database & Media Storage

#### Development

- SQLite3 — Simple database
- Local `MEDIA_ROOT` — Local media file storage

#### Production

- PostgreSQL — Object-relational database management system
- Cloudflare R2 — Near free, unstructured data storage system

## Development

### Frontend

```bash
cd frontend
npm install  # install the necessary dependencies
npm run dev
```

### Backend

```bash
cd backend
uv sync  # sync the virtual environment
uv run python manage.py migrate  # migrate database
uv run python manage.py runserver
```

### Database & Media Storage

You do not need a separate database or media storage for local development. The built-in SQLite3 in Django will work fine, and media files will be stored in your `MEDIA_ROOT`.

## GitHub Actions

The GitHub Actions CI/CD contains 3 components:

1. Backend lint: run ruff lint and format checks
2. Backend tests: run Django tests
3. Frontend lint: run ESLint, Prettier, and npm build

To run CI locally, use the command `make ci-local`; to run checks individually, use the following commands:

```bash
make lint  # lint code
make test  # run tests
make format-check  # check code formatting
```

## Deployment

The frontend, backend, and PostgreSQL database are deployed on [Render](https://www.render.com). The media storage and custom domain are bought from [Cloudflare](https://www.cloudflare.com).

- Frontend: a free static site
- Backend: a 0.5 CPU 512 MB RAM web service
- Database: 0.1 CPU 256 MB 10GB PostgreSQL service
- Media storage: Cloudflare R2 object storage service

## License

[MIT](LICENSE)
