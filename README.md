# TrayCycle

A camera-based plate-waste tracker for the SAS cafeteria, presented measured waste in kg per dish plus a forecast the kitchen can act on.

## Start the development server

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
source .venv/bin/activate  # activate the virtual environment
python manage.py migrate  # migrate database
python manage.py runserver
```

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

The frontend, backend, and PostgreSQL database are deployed on [Render](https://www.render.com). The media storage and custom domain are bought from [Cloudflare][https://www.cloudflare.com].

- Frontend: a free static site
- Backend: a 0.5 CPU 512 MB RAM web service
- Database: 0.1 CPU 256 MB 10GB PostgreSQL service
- Media storage: Cloudflare R2 object storage service
