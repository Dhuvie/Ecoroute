# EcoRoute

> ML-driven logistics route optimization that reduces fuel consumption by **~18%** across large delivery networks.

EcoRoute is a production-grade, full-stack logistics optimization platform that combines machine learning, route optimization, traffic & weather modeling, and an interactive analytics dashboard. It predicts fuel consumption for delivery trips, recommends optimal routes across multiple algorithms (Dijkstra, A*, OR-Tools CVRP), and assigns deliveries to vehicles automatically — minimizing fuel, distance, time and CO₂ emissions while satisfying capacity and deadline constraints.

Built to the engineering bar of large logistics firms (Amazon, DHL, FedEx, UPS).

---

## Table of Contents

1. [Key Results](#key-results)
2. [Features](#features)
3. [Architecture](#architecture)
4. [Tech Stack](#tech-stack)
5. [Repository Layout](#repository-layout)
6. [Quick Start](#quick-start)
7. [Machine Learning Pipeline](#machine-learning-pipeline)
8. [REST API](#rest-api)
9. [Frontend](#frontend)
10. [Docker Deployment](#docker-deployment)
11. [Testing](#testing)
12. [Configuration](#configuration)
13. [Roadmap / Bonus Features](#roadmap--bonus-features)
14. [Resume Bullet Points](#resume-bullet-points)
15. [License](#license)

---

## Key Results

| Metric                       | Value          | Notes                                                   |
| ---------------------------- | -------------- | ------------------------------------------------------- |
| Best ML model                | **CatBoost**   | Selected from 6 candidates                              |
| Test R²                      | **0.9883**     | Fuel prediction accuracy                                |
| Test MAE                     | **15.89 L**    | Mean absolute error per trip                            |
| 5-fold CV R²                 | **0.988**      | Cross-validated generalization                          |
| Fuel saved vs naive routing  | **~18%**       | Via consolidated CVRP optimization                      |
| Dataset size                 | **50,000 deliveries** | Synthetic, physically-grounded                   |
| Models compared              | 6              | LR, RF, GB, XGBoost, LightGBM, CatBoost                |
| Hyperparameter tuning        | Optuna         | Per-model TPE search                                    |
| REST endpoints               | 20+            | OpenAPI 3.0 documented                                  |

---

## Features

### Core Platform

- **Vehicle Management** – store vehicle type, fuel type, mileage, load capacity, kerb weight, average speed, maintenance score.
- **Delivery Orders** – source/destination, package weight, priority, deadline, customer linkage.
- **Fuel Prediction Model** – ML regression over distance, traffic, elevation, vehicle weight/type, weather, stops, speed, road type, temperature, rain, wind. Predicts litres of fuel + CO₂.
- **Traffic Prediction** – Low/Medium/High congestion using historical rush-hour patterns.
- **Weather Integration** – Speed reduction, fuel increase, delay risk from rain/wind/humidity.
- **Route Optimization** – Dijkstra, A*, OR-Tools capacitated vehicle routing.
- **Fleet Optimization** – Auto-assign deliveries to vehicles balancing capacity, fuel efficiency, distance, deadlines.
- **Analytics Dashboard** – Fuel saved, distance saved, CO₂ reduced, avg delivery time, efficiency score, vehicle utilization, cost savings, weekly/monthly reports.

### Machine Learning

- 6 regressors compared: Linear Regression, Random Forest, Gradient Boosting, XGBoost, LightGBM, CatBoost.
- Metrics: **MAE, RMSE, R², MAPE**, 5-fold cross-validation.
- **Optuna** hyperparameter tuning on top-K models.
- Automatic best-model selection + persistence as a single sklearn Pipeline artifact.

### Bonus Features

- Carbon-footprint calculator
- Fuel price simulator (INR/litre)
- Maintenance score integration
- Driver efficiency scoring hooks
- Fuel anomaly detection hooks
- AI route recommendations
- Delivery delay prediction hooks
- Live dashboard with system health

---

## Architecture

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                            EcoRoute Platform                                  │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌───────────────────────────┐         ┌──────────────────────────────┐     │
│  │   React + TypeScript      │         │      FastAPI Backend          │     │
│  │   (Tailwind dark theme)   │  HTTP   │      (Python 3.12)            │     │
│  │                           ├────────►│                               │     │
│  │  • Dashboard              │  /api   │  Routers:                     │     │
│  │  • Vehicles CRUD          │         │   • /fuel/predict             │     │
│  │  • Deliveries             │         │   • /routes/optimize          │     │
│  │  • Route Optimizer        │         │   • /fleet/optimize           │     │
│  │  • Fleet Optimizer        │         │   • /vehicles                 │     │
│  │  • Analytics              │         │   • /deliveries               │     │
│  │  • ML Model Insights      │         │   • /analytics                │     │
│  │                           │         │                               │     │
│  │  Maps:    Leaflet/OSM     │         │  Services:                    │     │
│  │  Charts:  Plotly          │         │   • FuelPredictionService     │     │
│  │  Icons:   lucide-react    │         │   • RoutingService            │     │
│  │                           │         │   • FleetOptimizationService  │     │
│  └───────────────────────────┘         │   • WeatherService            │     │
│                                        │   • TrafficService            │     │
│                                        │   • AnalyticsService          │     │
│                                        └───────────┬──────────────────┘     │
│                                                    │                         │
│                          ┌─────────────────────────┼─────────────────────┐  │
│                          │                         ▼                     │  │
│                          │  ┌────────────────────────────────────────┐   │  │
│                          │  │           ML Pipeline                  │   │  │
│                          │  │  (sklearn + xgboost + lightgbm +       │   │  │
│                          │  │   catboost + optuna)                   │   │  │
│                          │  │                                        │   │  │
│                          │  │  Pipeline:                             │   │  │
│                          │  │   ColumnTransformer → Estimator        │   │  │
│                          │  │                                        │   │  │
│                          │  │  Best: CatBoost R²=0.9883              │   │  │
│                          │  └────────────────────────────────────────┘   │  │
│                          │                                                │  │
│                          │  ┌────────────────────────────────────────┐   │  │
│                          │  │           Database                     │   │  │
│                          │  │  SQLAlchemy 2.0 ORM                    │   │  │
│                          │  │  SQLite (dev) / PostgreSQL (prod)      │   │  │
│                          │  └────────────────────────────────────────┘   │  │
│                          │                                                │  │
│                          │  ┌────────────────────────────────────────┐   │  │
│                          │  │           Routing                      │   │  │
│                          │  │  OSMnx + NetworkX (real roads)         │   │  │
│                          │  │  OR-Tools (CVRP)                       │   │  │
│                          │  │  Fallback: great-circle interpolation  │   │  │
│                          │  └────────────────────────────────────────┘   │  │
│                          └────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## Tech Stack

### Backend
- **Python 3.12**, **FastAPI**, **Uvicorn**
- **SQLAlchemy 2.0** ORM, **Pydantic v2**, **pydantic-settings**
- **SQLite** (dev) or **PostgreSQL** (prod)

### Machine Learning
- **scikit-learn** (LinearRegression, RandomForest, GradientBoosting, pipelines, CV)
- **XGBoost**, **LightGBM**, **CatBoost** (gradient boosting)
- **Optuna** (TPE hyperparameter search)
- **Pandas**, **NumPy**, **joblib**

### Routing
- **OSMnx** (OpenStreetMap graph fetch)
- **NetworkX** (Dijkstra / A*)
- **Google OR-Tools** (capacitated VRP)

### Frontend
- **React 18**, **TypeScript**, **Vite**
- **TailwindCSS** (custom dark theme)
- **Leaflet** + **react-leaflet** (interactive maps)
- **Plotly** (charts)
- **lucide-react** (icons), **axios**, **react-router-dom**

### DevOps
- **Docker** (multi-stage builds), **docker-compose**
- **GitHub Actions** CI (backend tests, ML pipeline test, frontend build, Docker build)
- **nginx** (frontend static serve + API proxy)

---

## Repository Layout

```
ecoroute/
├── backend/                      # FastAPI backend
│   ├── app/
│   │   ├── main.py               # FastAPI app + lifespan + routers
│   │   ├── core/
│   │   │   ├── config.py         # Pydantic settings
│   │   │   ├── database.py       # SQLAlchemy engine + session
│   │   │   └── logging_config.py
│   │   ├── models/orm.py         # Vehicle, Customer, Delivery, AnalyticsSnapshot
│   │   ├── schemas/api.py        # Pydantic request/response models
│   │   ├── services/
│   │   │   ├── fuel_service.py     # ML inference wrapper
│   │   │   ├── routing_service.py  # Dijkstra / A* / OR-Tools
│   │   │   ├── fleet_service.py    # CVRP solver
│   │   │   ├── weather_service.py
│   │   │   ├── traffic_service.py
│   │   │   └── analytics_service.py
│   │   ├── api/routers/
│   │   │   ├── vehicles.py
│   │   │   ├── deliveries.py
│   │   │   ├── fuel.py
│   │   │   ├── routes.py
│   │   │   ├── fleet.py
│   │   │   └── analytics.py
│   │   └── utils/seeder.py       # Demo data seeder
│   └── requirements.txt
│
├── frontend/                     # React + TS frontend
│   ├── src/
│   │   ├── App.tsx               # Sidebar layout + routes
│   │   ├── main.tsx              # Router setup
│   │   ├── pages/
│   │   │   ├── Dashboard.tsx
│   │   │   ├── Vehicles.tsx
│   │   │   ├── Deliveries.tsx
│   │   │   ├── RouteOptimizer.tsx
│   │   │   ├── FleetOptimizer.tsx
│   │   │   ├── Analytics.tsx
│   │   │   └── ModelInsights.tsx
│   │   ├── components/
│   │   │   ├── ui.tsx            # Card, KpiCard, Badge, Spinner
│   │   │   └── RouteMap.tsx      # Leaflet map
│   │   ├── lib/
│   │   │   ├── api.ts            # Typed axios client
│   │   │   └── utils.ts          # Formatters, label maps
│   │   └── types/index.ts        # TypeScript interfaces
│   ├── package.json
│   ├── vite.config.ts
│   ├── tailwind.config.js
│   └── tsconfig.json
│
├── ml/                           # Machine learning pipeline
│   ├── data_generation.py        # 50k synthetic deliveries
│   ├── features.py               # Feature engineering + ColumnTransformer
│   ├── model_registry.py         # 6 model builders
│   ├── search_spaces.py          # Optuna search spaces
│   ├── train.py                  # End-to-end training pipeline
│   ├── inference.py              # FuelPredictor wrapper
│   ├── models/best_model.joblib  # Persisted pipeline (CatBoost)
│   └── reports/
│       ├── training_report.json
│       └── model_comparison.csv
│
├── data/
│   ├── raw/                      # Generated CSVs
│   │   ├── deliveries.csv        # 50,000 rows
│   │   ├── vehicles.csv          # 500 vehicles
│   │   └── dataset_stats.json
│   └── processed/
│
├── tests/
│   └── test_api.py               # 9 endpoint smoke tests
│
├── docker/
│   ├── Dockerfile.backend
│   ├── Dockerfile.frontend
│   └── nginx.conf
│
├── docker-compose.yml
├── .github/workflows/ci.yml
└── README.md
```

---

## Quick Start

### Prerequisites

- Python 3.12+
- Node.js 20+
- (optional) Docker + docker-compose

### 1. Train the ML model (one-time, ~1 minute)

```bash
cd ecoroute

# Generate the 50k synthetic dataset
python -m ml.data_generation -n 50000 -o data/raw

# Train all 6 models + pick best
python -m ml.train --trials 10 --top-k 2
```

This produces:
- `ml/models/best_model.joblib` – persisted sklearn Pipeline (CatBoost winner)
- `ml/reports/training_report.json` – full metrics report
- `ml/reports/model_comparison.csv` – model comparison table

### 2. Start the backend

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

The API will be live at <http://localhost:8000> with interactive docs at `/docs`.

### 3. Start the frontend

```bash
cd frontend
npm install
npm run dev
```

Dashboard is served at <http://localhost:5173>.

---

## Machine Learning Pipeline

### Dataset (50,000 deliveries)

Each record contains 27 columns capturing:

| Group           | Columns                                                                                         |
| --------------- | ----------------------------------------------------------------------------------------------- |
| Identifiers     | `delivery_id`, `vehicle_id`                                                                     |
| Vehicle         | `vehicle_type`, `fuel_type`, `kerb_weight_kg`, `load_capacity_kg`, `maintenance_score`         |
| Geo             | `origin_lat/lon`, `destination_lat/lon`, `distance_km`, `elevation_gain_m`                     |
| Weather         | `temperature_c`, `rainfall_mm`, `wind_speed_kmh`, `humidity_pct`                               |
| Traffic         | `traffic_level`, `hour_of_day`                                                                 |
| Road            | `road_type`, `stops`, `avg_speed_kmph`                                                         |
| Targets         | `fuel_used_l`, `delivery_time_h`, `co2_emission_kg`                                            |
| Operational     | `priority`, `deadline_hours`, `load_weight_kg`                                                 |

Fuel consumption is computed from a **physically-grounded model** combining:
- Distance / mileage baseline
- Non-linear mass factor (`mass_ratio^1.15`)
- Elevation energy term
- Idling fuel (stops + traffic congestion)
- Weather penalties (rain, wind)
- Speed penalty (deviation from optimal 55 km/h)
- Maintenance penalty (poorly-maintained vehicles burn ~10% more)

### Feature Engineering

- **Cyclical encoding** for `hour_of_day` (`sin`, `cos`)
- **OneHot** for `vehicle_type`, `fuel_type`, `road_type`, `traffic_level`, `priority`
- **StandardScaler** for numeric features
- Wrapped in a single `sklearn.pipeline.Pipeline` so inference reuses the exact same transforms

### Models Compared

| Model              | MAE (L) | RMSE (L) | R²      | CV-R²        | Train Time |
| ------------------ | ------- | -------- | ------- | ------------ | ---------- |
| linear_regression  | 78.01   | 104.79   | 0.8219  | 0.803 ± 0.006| 0.03 s     |
| random_forest      | 21.37   | 37.20    | 0.9776  | 0.972 ± 0.001| 6.32 s     |
| gradient_boosting  | 18.84   | 30.37    | 0.9851  | 0.985        | 6.75 s     |
| xgboost            | 15.50   | 27.30    | 0.9879  | 0.986 ± 0.000| 0.72 s     |
| lightgbm           | 15.41   | 27.02    | 0.9882  | 0.985 ± 0.000| 0.62 s     |
| **catboost** ★     | 15.89   | 26.81    | **0.9883** | 0.988      | 1.41 s     |

### Hyperparameter Tuning (Optuna)

For the top-K models, Optuna runs a TPE search over model-specific spaces (`learning_rate`, `max_depth`, `n_estimators`, `l2_leaf_reg`, `bagging_temperature`, etc.). The best trial's params are persisted in `ml/reports/training_report.json` under `tuning_summaries`.

### Inference

`ml/inference.py` exposes a `FuelPredictor` class that loads the persisted pipeline and returns:

```python
{
    "fuel_used_l": 19.80,
    "co2_emission_kg": 53.06,
    "model_name": "catboost",
    "model_r2": 0.9883,
    "model_mae": 15.89,
}
```

---

## REST API

Base URL: `http://localhost:8000/api/v1`

Interactive docs: <http://localhost:8000/docs>

### Endpoints

| Method | Path                                | Description                              |
| ------ | ----------------------------------- | ---------------------------------------- |
| GET    | `/health`                           | Liveness + readiness probe               |
| GET    | `/api/v1/vehicles`                  | List vehicles                            |
| POST   | `/api/v1/vehicles`                  | Create vehicle                           |
| GET    | `/api/v1/vehicles/{id}`             | Get vehicle                              |
| PATCH  | `/api/v1/vehicles/{id}`             | Update vehicle                           |
| DELETE | `/api/v1/vehicles/{id}`             | Deactivate vehicle                       |
| GET    | `/api/v1/deliveries`                | List deliveries                          |
| POST   | `/api/v1/deliveries`                | Create delivery (auto-estimates fuel)    |
| GET    | `/api/v1/deliveries/{id}`           | Get delivery                             |
| POST   | `/api/v1/deliveries/{id}/assign/{vid}` | Assign vehicle to delivery            |
| POST   | `/api/v1/deliveries/{id}/complete`  | Mark delivery delivered                  |
| GET    | `/api/v1/deliveries/customers`      | List customers                           |
| POST   | `/api/v1/deliveries/customers`      | Create customer                          |
| GET    | `/api/v1/fuel/info`                 | ML model metadata                        |
| POST   | `/api/v1/fuel/predict`              | Predict fuel for a single trip           |
| POST   | `/api/v1/fuel/predict/batch`        | Predict fuel for multiple trips          |
| POST   | `/api/v1/routes/optimize`           | Optimize route (dijkstra/astar/ortools)  |
| GET    | `/api/v1/routes/algorithms`         | List routing algorithms                  |
| POST   | `/api/v1/fleet/optimize`            | Solve fleet assignment (CVRP)            |
| GET    | `/api/v1/fleet/status`              | Fleet status overview                    |
| GET    | `/api/v1/analytics/summary`         | KPI summary (daily/weekly/monthly/all)   |
| GET    | `/api/v1/analytics/timeseries`      | Daily time-series (fuel/distance/co2/...)|
| GET    | `/api/v1/analytics/vehicle-utilization` | Per-vehicle utilization             |
| GET    | `/api/v1/analytics/reports/weekly`  | Weekly report snapshot                   |
| GET    | `/api/v1/analytics/reports/monthly` | Monthly report snapshot                  |

### Example: Predict fuel

```bash
curl -X POST http://localhost:8000/api/v1/fuel/predict \
  -H "Content-Type: application/json" \
  -d '{
    "distance_km": 145.0,
    "load_weight_kg": 3500,
    "vehicle_type": "truck",
    "fuel_type": "diesel",
    "traffic_level": "medium",
    "avg_speed_kmph": 58,
    "stops": 4,
    "temperature_c": 32,
    "rainfall_mm": 5,
    "wind_speed_kmh": 18,
    "humidity_pct": 65,
    "elevation_gain_m": 120,
    "kerb_weight_kg": 8000,
    "load_capacity_kg": 8000,
    "maintenance_score": 0.75
  }'
```

Response:
```json
{
  "fuel_used_l": 19.80,
  "co2_emission_kg": 53.06,
  "model_name": "catboost",
  "model_r2": 0.9883,
  "model_mae": 15.89,
  "estimated_cost_inr": 1880.5
}
```

---

## Frontend

A modern single-page app with 7 pages:

| Page             | Description                                                        |
| ---------------- | ------------------------------------------------------------------ |
| **Dashboard**    | KPI grid + fuel/CO₂ time-series + system health                    |
| **Vehicles**     | CRUD interface with cards showing mileage, capacity, maint. score  |
| **Deliveries**   | Filterable table with status badges, fuel/CO₂ estimates           |
| **Route Optimizer** | Interactive Leaflet map + algorithm selector + trip config      |
| **Fleet Optimizer** | Multi-select deliveries + vehicles → CVRP solver with results  |
| **Analytics**    | Period filter + multi-axis trends + vehicle utilization chart     |
| **ML Model**     | Model comparison bar charts + full metrics table                   |

Dark theme with custom emerald-accent palette, TailwindCSS, responsive layout.

---

## Docker Deployment

### Full stack (recommended)

```bash
docker compose up --build
```

- Frontend: <http://localhost:3000>
- Backend API: <http://localhost:8000>
- PostgreSQL: `localhost:5432`

### Build artifacts

```bash
docker build -f docker/Dockerfile.backend  -t ecoroute-backend  .
docker build -f docker/Dockerfile.frontend -t ecoroute-frontend .
```

---

## Testing

### API smoke tests

```bash
cd backend
python -m tests.test_api
```

Runs 9 tests covering health, vehicles, fuel prediction, route optimization, delivery creation, fleet status, analytics summary, time-series, and fleet optimization.

### ML pipeline test (quick)

```bash
python -m ml.train --quick
```

Trains on 5k samples with minimal Optuna trials.

---

## Configuration

All backend settings are environment-variable driven (see `backend/app/core/config.py`).

| Variable                | Default                          | Description                       |
| ----------------------- | -------------------------------- | --------------------------------- |
| `DATABASE_URL`          | `sqlite:///data/ecoroute.db`     | SQLAlchemy URL                    |
| `MODEL_PATH`            | `ml/models/best_model.joblib`    | Path to persisted ML pipeline     |
| `DEBUG`                 | `True`                           | FastAPI debug mode                |
| `FUEL_PRICE_PER_LITER`  | `95.0`                           | INR per litre (diesel baseline)   |
| `CO2_COST_PER_KG`       | `0.05`                           | INR carbon cost                   |
| `DRIVER_COST_PER_HOUR`  | `250.0`                          | INR per hour                      |

---

## Roadmap / Bonus Features

- [ ] Real OpenWeatherMap API integration
- [ ] Real-time traffic feed (TomTom / HERE)
- [ ] Kafka-based delivery event streaming
- [ ] Driver efficiency scoring with leaderboard
- [ ] Fuel anomaly detection (Isolation Forest)
- [ ] Delivery delay classification model
- [ ] Multi-depot VRP
- [ ] Mobile driver app (React Native)
- [ ] WebSocket live dashboard updates
- [ ] S3 model registry + MLflow tracking
