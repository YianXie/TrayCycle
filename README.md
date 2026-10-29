# TrayCycle

A camera-based plate-waste tracker for the SAS cafeteria, presented measured waste in kg per dish plus a forecast the kitchen can act on.

## Start the development server

### Frontend

```bash
cd frontend
npm install  # install the necessary dependencies
npm run dev
```

The frontend uses React and typescript, with Vite for deployment and builds, Material UI for interface components, and Toolpad Core as the dashboard layout. API requests uses Axios.

Create frontend/.env.local with
```dotenv
VITE_API_URL=http://localhost:8000
```
Note that this assumes that Django runs on 8000 and is running for backend features. Restart Vite after changing environment variables. VITE_ is exposed to frontend code so do not put secrets into it.

Where things are:
frontend/
├── src/
│   ├── pages/              Page components: Home, About Us and a unused Upload page
│   ├── components/layout/  Shared layout components
│   ├── styles/             Page-specific CSS
│   ├── api.ts              Shared Axios client and authentication handling
│   ├── App.tsx             Application routing
│   └── main.tsx            React entry point
├── public/                 Public static assets
└── package.json            Dependencies and development commands

* Note that the upload function was removed because our school banned phones.

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

The frontend, backend, and PostgreSQL database are deployed on [Render](https://www.render.com). The media storage and custom domain are bought from [Cloudflare](https://www.cloudflare.com).

- Frontend: a free static site
- Backend: a 0.5 CPU 512 MB RAM web service
- Database: 0.1 CPU 256 MB 10GB PostgreSQL service
- Media storage: Cloudflare R2 object storage service
