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
