# Voice AI Patient Registration System

A take-home assessment prototype for a voice-based patient registration agent. The system exposes a validated REST API, persists patient records, supports soft deletion, and includes a simple dashboard.

## Architecture

Vapi voice agent → `POST /patients` → FastAPI/Pydantic validation → PostgreSQL or SQLite → Dashboard

The voice provider is intentionally decoupled from the backend. Configure a Vapi assistant with a `create_patient` tool that sends the confirmed structured payload to the deployed `/patients` endpoint.

## Features

- Required and optional patient fields
- Server-side validation for DOB, phone, state, ZIP, names, and email
- Confirmation-before-save workflow supported by the voice prompt
- CRUD REST API
- Duplicate detection by active phone number
- Soft delete
- OpenAPI/Swagger documentation
- Basic dashboard at `/dashboard/`
- Health endpoint at `/health`

## Local setup

```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
copy .env.example .env  # Windows
# cp .env.example .env  # macOS/Linux
uvicorn app.main:app --reload
```

Open `http://localhost:8000/docs` and `http://localhost:8000/dashboard/`.

## Environment variables

- `DATABASE_URL`: SQLite for local development or PostgreSQL URL for deployment
- `APP_ENV`: environment name
- `CORS_ORIGINS`: comma-separated origins, or `*` for assessment use

## API endpoints

- `GET /health`
- `POST /patients`
- `GET /patients`
- `GET /patients/{patient_id}`
- `PUT /patients/{patient_id}`
- `DELETE /patients/{patient_id}`

## Vapi tool configuration

Create a tool named `create_patient` with the same JSON properties as the `POST /patients` request schema. Configure it to call:

```text
https://YOUR-DEPLOYED-APP/patients
```

The assistant should only call the tool after all required fields are collected and the caller confirms the read-back. If the API returns a 409, explain that a record already exists. If it returns an error, do not claim success.

## Sample request

```json
{
  "first_name": "Jane",
  "last_name": "Doe",
  "date_of_birth": "1990-05-15",
  "sex": "Female",
  "phone_number": "5551234567",
  "email": "jane@example.com",
  "address_line_1": "123 Main Street",
  "city": "New York",
  "state": "NY",
  "zip_code": "10001"
}
```

## Testing

```bash
pytest -q
```

## Deployment

Deploy this repository to Railway, Render, or another Python host. For production-like persistence, add a PostgreSQL service and set `DATABASE_URL` to the provider's connection string. The Dockerfile is included for container-based deployment.

## Privacy note

This is an assessment prototype. Use dummy data only. A production healthcare deployment would require HIPAA-compliant infrastructure, encryption, authentication/authorization, PHI-safe logs, audit trails, retention controls, and appropriate vendor agreements.
