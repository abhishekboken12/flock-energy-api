# Flock Energy API Wrapper

A REST API wrapper for the legacy Urja Meter Ops portal. This service exposes meter information, geographic coordinates, and energy readings through documented FastAPI endpoints.

## Features

- List and search meters with pagination.
- Retrieve normalized meter details and hierarchy.
- Retrieve meter geographic coordinates.
- Retrieve energy readings, including kWh, kVAh, and voltage.
- Interactive API documentation through Swagger UI.

## Tech Stack

- Python 3.12+
- FastAPI
- Uvicorn
- HTTPX
- python-dotenv

## Project Structure

```text
flock-energy-api/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── client.py
│   ├── models.py
│   └── config.py
├── .env
├── .gitignore
├── requirements.txt
├── README.md
├── PROTOCOL.md
├── REFLECTION.md
└── openapi.json
```

## Setup

### 1. Create and activate a virtual environment

```bash
python3.12 -m venv .venv
source .venv/bin/activate
```

### 2. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 3. Configure the portal session

Create a `.env` file in the project root:

```env
URJA_SESSION_COOKIE=your_session_cookie_value
```

Use a valid session cookie obtained through your own authorized portal login. Keep `.env` private and never commit it to Git.

### 4. Run the API

```bash
uvicorn app.main:app --reload
```

The API runs at `http://127.0.0.1:8000`.

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/v1/meters?page=1&q=` | List or search meters |
| GET | `/api/v1/meters/{meter_id}` | Retrieve normalized meter details |
| GET | `/api/v1/meters/{meter_id}/geo` | Retrieve meter coordinates |
| GET | `/api/v1/meters/{meter_id}/energy` | Retrieve energy readings |

### Interactive documentation

After starting the server, visit:

- Swagger UI: `http://127.0.0.1:8000/docs`
- OpenAPI schema: `http://127.0.0.1:8000/openapi.json`

## Authentication and Data Access

The wrapper uses a session cookie to make requests to the legacy portal. The session must be valid and authorized to access the requested data. The wrapper does not modify meter data.

## Error Handling

The API translates upstream HTTP errors into HTTP responses and reports request or configuration failures through FastAPI error responses. Check the response body for the error details.

## Security

- Never commit `.env` or session cookies.
- Use only authorized portal access.
- Refresh expired sessions when necessary.
- Do not expose credentials in logs, screenshots, or public repositories.

## Current Status

The four primary API endpoints have been tested locally and returned HTTP 200 OK.
