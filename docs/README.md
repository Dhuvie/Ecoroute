# EcoRoute Documentation Index

| Document | Description |
| --- | --- |
| [README.md](../README.md) | Project overview, quick start, results, resume bullets |
| [API.md](API.md) | Full REST API reference with examples |
| [DEPLOYMENT.md](DEPLOYMENT.md) | Local, Docker Compose, and Kubernetes deployment guides |
| [ARCHITECTURE.md](ARCHITECTURE.md) | Mermaid architecture + sequence + ML pipeline diagrams |

## Quick Links

- **Run the backend**: `cd backend && uvicorn app.main:app --reload --port 8000`
- **Run the frontend**: `cd frontend && npm run dev`
- **Train ML model**: `python -m ml.train --trials 10 --top-k 2`
- **Run tests**: `cd backend && python -m tests.test_api`
- **Docker full stack**: `docker compose up --build`

## API Docs (when running)

- Swagger UI: <http://localhost:8000/docs>
- ReDoc: <http://localhost:8000/redoc>
- OpenAPI JSON: <http://localhost:8000/openapi.json>
