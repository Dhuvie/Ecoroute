# EcoRoute Deployment Guide

This guide covers three deployment scenarios:

1. **Local development** – fastest iteration loop
2. **Docker Compose** – single-host production
3. **Production Kubernetes** – scalable multi-node deployment

---

## 1. Local Development

### Prerequisites

- Python 3.12+
- Node.js 20+
- (optional) PostgreSQL 16+

### Step-by-step

```bash
# 1. Clone the repo
git clone https://github.com/your-org/ecoroute.git
cd ecoroute

# 2. Train the ML model (one-time, ~1 min)
python -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
python -m ml.data_generation -n 50000 -o data/raw
python -m ml.train --trials 10 --top-k 2

# 3. Start the backend
cd backend
uvicorn app.main:app --reload --port 8000

# 4. In a new terminal, start the frontend
cd frontend
npm install
npm run dev
# -> http://localhost:5173
```

---

## 2. Docker Compose (Single-Host Production)

### Prerequisites

- Docker 24+
- docker-compose v2+

### Deploy

```bash
docker compose up --build -d
```

This starts three containers:

| Service   | Port | Description                          |
| --------- | ---- | ------------------------------------ |
| backend   | 8000 | FastAPI + Uvicorn                    |
| frontend  | 3000 | nginx serving built React app        |
| db        | 5432 | PostgreSQL 16                        |

### Verify

```bash
curl http://localhost:8000/health
curl http://localhost:3000/
```

### View logs

```bash
docker compose logs -f backend
docker compose logs -f frontend
```

### Stop

```bash
docker compose down
# With data wipe:
docker compose down -v
```

---

## 3. Production Kubernetes

### Backend deployment

```yaml
# k8s/backend-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ecoroute-backend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: ecoroute-backend
  template:
    metadata:
      labels:
        app: ecoroute-backend
    spec:
      containers:
      - name: backend
        image: your-registry/ecoroute-backend:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: ecoroute-secrets
              key: database-url
        - name: MODEL_PATH
          value: /app/ml/models/best_model.joblib
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: ecoroute-backend
spec:
  selector:
    app: ecoroute-backend
  ports:
  - port: 8000
    targetPort: 8000
```

### Frontend deployment

```yaml
# k8s/frontend-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ecoroute-frontend
spec:
  replicas: 2
  selector:
    matchLabels:
      app: ecoroute-frontend
  template:
    metadata:
      labels:
        app: ecoroute-frontend
    spec:
      containers:
      - name: frontend
        image: your-registry/ecoroute-frontend:latest
        ports:
        - containerPort: 80
        resources:
          requests:
            memory: "128Mi"
            cpu: "100m"
          limits:
            memory: "256Mi"
            cpu: "250m"
---
apiVersion: v1
kind: Service
metadata:
  name: ecoroute-frontend
spec:
  type: LoadBalancer
  selector:
    app: ecoroute-frontend
  ports:
  - port: 80
    targetPort: 80
```

### Ingress

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: ecoroute-ingress
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  rules:
  - host: ecoroute.example.com
    http:
      paths:
      - path: /api
        pathType: Prefix
        backend:
          service:
            name: ecoroute-backend
            port:
              number: 8000
      - path: /
        pathType: Prefix
        backend:
          service:
            name: ecoroute-frontend
            port:
              number: 80
```

---

## Environment Variables

| Variable                | Default                          | Description                       |
| ----------------------- | -------------------------------- | --------------------------------- |
| `DATABASE_URL`          | `sqlite:///data/ecoroute.db`     | SQLAlchemy URL                    |
| `MODEL_PATH`            | `ml/models/best_model.joblib`    | Path to persisted ML pipeline     |
| `DEBUG`                 | `True`                           | FastAPI debug mode                |
| `FUEL_PRICE_PER_LITER`  | `95.0`                           | INR per litre (diesel baseline)   |
| `CO2_COST_PER_KG`       | `0.05`                           | INR carbon cost                   |
| `DRIVER_COST_PER_HOUR`  | `250.0`                          | INR per hour                      |
| `CORS_ORIGINS`          | `http://localhost:3000,5173`     | Comma-separated allowed origins   |

---

## Scaling Considerations

### Backend

- **Horizontal scaling**: FastAPI is stateless; scale by adding pods. Use a shared PostgreSQL/Redis.
- **ML inference**: CatBoost model is ~570 KB on disk; load once per process. For high QPS, run a Triton Inference Server sidecar.
- **OSMnx cache**: persist `/app/data/osm_cache` to a PVC to avoid re-downloading graphs.

### Frontend

- Static assets, infinitely scalable via CDN.
- Plotly bundle is ~5 MB; consider `react-plotly.js/factory` + lazy loading for faster TTI.

### Database

- For >1M deliveries, add indexes on `deliveries.status`, `deliveries.vehicle_id`, `deliveries.created_at`.
- Partition `deliveries` by month for time-series queries.

---

## Monitoring

- **Health**: `GET /health` returns model + DB readiness.
- **Metrics**: integrate Prometheus via `prometheus-fastapi-instrumentator`.
- **Logs**: structured JSON logs to stdout, ship via Fluentd/Filebeat.
- **Tracing**: OpenTelemetry SDK with Jaeger backend.

---

## Security Checklist

- [ ] Add OAuth2 / JWT authentication
- [ ] Enable HTTPS (Let's Encrypt + cert-manager)
- [ ] Add rate limiting (`slowapi`)
- [ ] Enable CORS allowlist for production domain
- [ ] Rotate database credentials via Vault
- [ ] Add CSRF protection for cookie-based auth
- [ ] Audit log for vehicle/delivery mutations
- [ ] Encrypt `model_path` artifacts at rest (KMS)
