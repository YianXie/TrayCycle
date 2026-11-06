# TrayCycle

> By team TriCycle (Ian Xie, Gordon Ji, Aryan Mahajan), for 2026-2027 SAS CSHS Hackathon.

A camera-based food-waste tracker for the SAS cafeteria, presented measured waste in kg per dish plus a dashboard the kitchen can act on.

Live site: [traycycle.org](https://traycycle.org)

## Preview

![TrayCycle about-us page](assets/preview.png)

## Tech stack

### Frontend

- React — Framework
- MUI — UI library
- Vite — Build tool + dev server
- Axios — Handles API requests
- React Router — Client-side routing

**File tree:**

```
├── 📁 public
│   ├── 🖼️ favicon.svg
│   ├── 🖼️ icons.svg
│   └── 🖼️ traycycle-scan.svg
├── 📁 src
│   ├── 📁 assets
│   │   ├── 🖼️ hero.png
│   │   ├── 🖼️ react.svg
│   │   └── 🖼️ vite.svg
│   ├── 📁 components
│   │   └── 📁 layout
│   │       ├── 📄 Header.tsx
│   │       └── 📄 Layout.tsx
│   ├── 📁 pages
│   │   ├── 📄 AboutUs.tsx
│   │   ├── 📄 Dashboard.tsx
│   │   ├── 📄 Home.tsx
│   │   └── 📄 Upload.tsx
│   ├── 📁 styles
│   │   ├── 🎨 AboutUs.css
│   │   └── 🎨 Upload.css
│   ├── 🎨 App.css
│   ├── 📄 App.tsx
│   ├── 📄 UsePageTitle.tsx
│   ├── 📄 api.ts
│   ├── 🎨 index.css
│   └── 📄 main.tsx
├── ⚙️ .prettierignore
├── ⚙️ .prettierrc
├── 📄 eslint.config.js
├── 🌐 index.html
├── ⚙️ package-lock.json
├── ⚙️ package.json
├── ⚙️ tsconfig.app.json
├── ⚙️ tsconfig.json
├── ⚙️ tsconfig.node.json
└── 📄 vite.config.ts
```

### Backend

- Django — Base framework
- Django Rest Framework — RESTful APIs, viewsets, and serializers
- uv — Python dependencies management
- django-filter — Create dynamic filter rules in URL query parameters

**Endpoints:**

|       **Method**        |           **Endpoint**           |                   **Description**                    |    **Auth**     |
| :---------------------: | :------------------------------: | :--------------------------------------------------: | :-------------: |
|          POST           |        `/api-token-auth`         |                Obtain the auth token                 |      None       |
|        GET, POST        |         `/api/stations`          |               List or create stations                |      Staff      |
| GET, PUT, PATCH, DELETE |       `/api/stations/{id}`       |          Read, update, or delete a station           |      Staff      |
|        GET, POST        |          `/api/dishes`           |                List or create dishes                 |      Staff      |
| GET, PUT, PATCH, DELETE |        `/api/dishes/{id}`        |            Read, update, or delete a dish            |      Staff      |
|           GET           |           `/api/menus`           |                   List menu items                    | Staff or worker |
|           GET           |       `/api/menus/{date}`        |                Retrieve menu on a day                | Staff or worker |
|          POST           |           `/api/menus`           |                  Create menu items                   |      Staff      |
|   PUT, PATCH, DELETE    |       `/api/menus/{date}`        |         Update or delete a menu day instance         |      Staff      |
|        POST, GET        |          `/api/devices`          |                List or create devices                |      Staff      |
| GET, PUT, PATCH, DELETE |       `/api/devices/{id}`        |           Read, update, or delete a device           |      Staff      |
|          POST           | `/api/devices/{id}/rotate-token` |               Rotate a device's token                |      Staff      |
|           GET           |         `/api/captures`          |                    List captures                     |      Staff      |
|          POST           |         `/api/captures`          |                   Create a capture                   | Staff or device |
| GET, PUT, PATCH, DELETE |       `/api/captures/{id}`       |          Read, update, or delete a capture           |      Staff      |
|          POST           |    `/api/captures/{id}/claim`    |              Claim a capture to process              | Staff or worker |
|          POST           |    `/api/captures/{id}/fail`     |               Set a capture as failed                | Staff or worker |
|           GET           |        `/api/predictions`        |                   Read predictions                   |      Staff      |
|          POST           |        `/api/predictions`        |                 Create a prediction                  | Staff or worker |
| GET, PUT, PATCH, DELETE |     `/api/predictions/{id}`      |         Read, update, or delete a prediction         |      Staff      |
|        GET, POST        |          `/api/labels`           |                List or create labels                 |      Staff      |
| GET, PUT, PATCH, DELETE |        `/api/labels/{id}`        |           Read, update, or delete a label            |      Staff      |
|        GET, POST        |    `/api/overproduction/{id}`    |          List or create overproduction logs          |      Staff      |
| GET, PUT, PATCH, DELETE |    `/api/overproduction/{id}`    |     Read, update, or delete a overproduction log     |      Staff      |
|           GET           |           `/api/stats`           | Fetch prediction stats based on the provided filters |      Staff      |
|           GET           |         `/api/forecast`          |          Fetch forecast of waste data (WIP)          |      Staff      |

<details>
<summary><b>Example `/api/stats` return response:</b></summary>

```json
{
  "bowl_count": 5,
  "average_waste_percent": 35.0,
  "total_waste_kg": 0.6,
  "average_waste_kg": 0.12,
  "daily": [
    {
      "date": "2025-12-01",
      "bowl_count": 1,
      "average_waste_percent": 25.0,
      "total_waste_kg": 0.062,
      "average_waste_kg": 0.062
    },
    {
      "date": "2025-12-02",
      "bowl_count": 1,
      "average_waste_percent": 0.0,
      "total_waste_kg": 0.0,
      "average_waste_kg": 0.0
    },
    {
      "date": "2025-12-03",
      "bowl_count": 1,
      "average_waste_percent": 75.0,
      "total_waste_kg": 0.263,
      "average_waste_kg": 0.263
    },
    {
      "date": "2025-12-04",
      "bowl_count": 1,
      "average_waste_percent": 50.0,
      "total_waste_kg": 0.2,
      "average_waste_kg": 0.2
    },
    {
      "date": "2025-12-05",
      "bowl_count": 1,
      "average_waste_percent": 25.0,
      "total_waste_kg": 0.075,
      "average_waste_kg": 0.075
    }
  ],
  "dishes": [
    {
      "dish_id": 14,
      "dish_name": "Beef Bulgogi",
      "bowl_count": 1,
      "average_waste_percent": 75.0,
      "total_waste_kg": 0.263,
      "average_waste_kg": 0.263,
      "daily": [
        {
          "date": "2025-12-03",
          "bowl_count": 1,
          "average_waste_percent": 75.0,
          "total_waste_kg": 0.263,
          "average_waste_kg": 0.263
        }
      ],
      "waste_bucket_distribution": {
        "75": 1
      }
    },
    {
      "dish_id": 18,
      "dish_name": "Hainanese Chicken Rice",
      "bowl_count": 1,
      "average_waste_percent": 50.0,
      "total_waste_kg": 0.2,
      "average_waste_kg": 0.2,
      "daily": [
        {
          "date": "2025-12-04",
          "bowl_count": 1,
          "average_waste_percent": 50.0,
          "total_waste_kg": 0.2,
          "average_waste_kg": 0.2
        }
      ],
      "waste_bucket_distribution": {
        "50": 1
      }
    },
    {
      "dish_id": 15,
      "dish_name": "Sweet and sour pork",
      "bowl_count": 1,
      "average_waste_percent": 25.0,
      "total_waste_kg": 0.075,
      "average_waste_kg": 0.075,
      "daily": [
        {
          "date": "2025-12-05",
          "bowl_count": 1,
          "average_waste_percent": 25.0,
          "total_waste_kg": 0.075,
          "average_waste_kg": 0.075
        }
      ],
      "waste_bucket_distribution": {
        "25": 1
      }
    },
    {
      "dish_id": 13,
      "dish_name": "Chicken Teriyaki",
      "bowl_count": 1,
      "average_waste_percent": 25.0,
      "total_waste_kg": 0.062,
      "average_waste_kg": 0.062,
      "daily": [
        {
          "date": "2025-12-01",
          "bowl_count": 1,
          "average_waste_percent": 25.0,
          "total_waste_kg": 0.062,
          "average_waste_kg": 0.062
        }
      ],
      "waste_bucket_distribution": {
        "25": 1
      }
    },
    {
      "dish_id": 16,
      "dish_name": "Caesar Salad",
      "bowl_count": 1,
      "average_waste_percent": 0.0,
      "total_waste_kg": 0.0,
      "average_waste_kg": 0.0,
      "daily": [
        {
          "date": "2025-12-02",
          "bowl_count": 1,
          "average_waste_percent": 0.0,
          "total_waste_kg": 0.0,
          "average_waste_kg": 0.0
        }
      ],
      "waste_bucket_distribution": {
        "0": 1
      }
    }
  ]
}
```

</details>

<br>

**File tree:**

```
├── 📁 core
│   ├── 🐍 __init__.py
│   ├── 🐍 asgi.py
│   ├── 🐍 settings.py
│   ├── 🐍 urls.py
│   └── 🐍 wsgi.py
├── 📁 waste
│   ├── 📁 management
│   │   ├── 📁 commands
│   │   │   ├── 🐍 __init__.py
│   │   │   ├── 🐍 create_worker.py
│   │   │   └── 🐍 seed_demo.py
│   │   └── 🐍 __init__.py
│   ├── 📁 tests
│   │   ├── 🐍 __init__.py
│   │   ├── 🐍 shared.py
│   │   ├── 🐍 test_captures.py
│   │   ├── 🐍 test_commands.py
│   │   ├── 🐍 test_devices.py
│   │   ├── 🐍 test_dishes.py
│   │   ├── 🐍 test_labels.py
│   │   ├── 🐍 test_menu_days.py
│   │   ├── 🐍 test_overproduction_logs.py
│   │   ├── 🐍 test_predictions.py
│   │   ├── 🐍 test_stations.py
│   │   ├── 🐍 test_stats.py
│   │   ├── 🐍 test_users.py
│   │   └── 🐍 test_workers.py
│   ├── 🐍 __init__.py
│   ├── 🐍 admin.py
│   ├── 🐍 apps.py
│   ├── 🐍 authentication.py
│   ├── 🐍 constants.py
│   ├── 🐍 exceptions.py
│   ├── 🐍 filters.py
│   ├── 🐍 models.py
│   ├── 🐍 pagination.py
│   ├── 🐍 permissions.py
│   ├── 🐍 serializers.py
│   ├── 🐍 urls.py
│   └── 🐍 views.py
├── ⚙️ .env.example
├── 📄 build.sh
├── 📄 db.sqlite3
├── 🐍 manage.py
├── ⚙️ pyproject.toml
└── 📄 uv.lock
```

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
