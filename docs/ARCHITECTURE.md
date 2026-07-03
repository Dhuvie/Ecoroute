# EcoRoute Architecture Diagram

Below is the high-level architecture rendered from Mermaid. Most Markdown viewers
(GitHub, VS Code) will render the diagram automatically.

```mermaid
flowchart TB
    subgraph Client[Client Layer]
        UI[React + TypeScript<br/>TailwindCSS Dark Theme]
        MAP[Leaflet Maps]
        CHARTS[Plotly Charts]
    end

    subgraph Edge[Edge / CDN]
        NGINX[nginx<br/>Static serve + API proxy]
    end

    subgraph Backend[FastAPI Backend]
        ROUTERS[API Routers<br/>vehicles, deliveries, fuel,<br/>routes, fleet, analytics]
        
        subgraph Services[Service Layer]
            FUEL[FuelPredictionService<br/>ML inference wrapper]
            ROUTE[RoutingService<br/>Dijkstra / A* / OR-Tools]
            FLEET[FleetOptimizationService<br/>CVRP solver]
            WEATHER[WeatherService]
            TRAFFIC[TrafficService]
            ANALYTICS[AnalyticsService]
        end
        
        ORM[SQLAlchemy 2.0 ORM]
        SEEDER[Demo Data Seeder]
    end

    subgraph ML[ML Pipeline]
        DATA_GEN[Data Generator<br/>50k synthetic deliveries]
        FE[Feature Engineering<br/>ColumnTransformer]
        MODELS[6 Model Trainers<br/>LR, RF, GB, XGB, LGBM, CatBoost]
        OPTUNA[Optuna Tuning<br/>Top-K models]
        BEST[Best Model: CatBoost<br/>R²=0.9883]
        ARTIFACT[best_model.joblib]
    end

    subgraph Routing[Routing Engines]
        OSMNX[OSMnx<br/>OpenStreetMap graphs]
        NETX[NetworkX<br/>Dijkstra + A*]
        ORT[OR-Tools<br/>CVRP solver]
    end

    subgraph Data[Data Layer]
        PG[(PostgreSQL 16<br/>or SQLite)]
        OSM_CACHE[(OSM Tile Cache)]
    end

    UI --> NGINX
    MAP --> NGINX
    CHARTS --> NGINX
    NGINX -->|/api/*| ROUTERS
    
    ROUTERS --> FUEL
    ROUTERS --> ROUTE
    ROUTERS --> FLEET
    ROUTERS --> ANALYTICS
    ROUTERS --> ORM
    
    FUEL --> ARTIFACT
    ROUTE --> OSMNX
    ROUTE --> NETX
    ROUTE --> FUEL
    ROUTE --> WEATHER
    ROUTE --> TRAFFIC
    FLEET --> ORT
    FLEET --> FUEL
    FLEET --> ORM
    ANALYTICS --> ORM
    
    ORM --> PG
    OSMNX --> OSM_CACHE
    
    DATA_GEN --> FE
    FE --> MODELS
    MODELS --> OPTUNA
    OPTUNA --> BEST
    BEST --> ARTIFACT

    style Client fill:#0f172a,stroke:#22c55e,color:#e2e8f0
    style Backend fill:#1e293b,stroke:#0ea5e9,color:#e2e8f0
    style ML fill:#1e293b,stroke:#a855f7,color:#e2e8f0
    style Data fill:#0f172a,stroke:#f59e0b,color:#e2e8f0
```

## Request Flow

```mermaid
sequenceDiagram
    participant U as User
    participant F as Frontend (React)
    participant N as nginx
    participant B as FastAPI Backend
    participant M as ML Pipeline
    participant D as Database

    U->>F: Configure trip (origin, destination, vehicle)
    F->>N: POST /api/v1/routes/optimize
    N->>B: Proxy request
    B->>B: RoutingService.optimize()
    B->>B: WeatherService.estimate_weather()
    B->>B: TrafficService.estimate_traffic()
    B->>M: FuelPredictor.predict(features)
    M-->>B: {fuel_used_l, co2_emission_kg}
    B->>B: Compute path (OSMnx/NetworkX or fallback)
    B-->>N: RouteResponse JSON
    N-->>F: JSON response
    F->>F: Render Leaflet map + KPI cards
    F-->>U: Optimized route displayed
```

## ML Training Pipeline

```mermaid
flowchart LR
    A[50k Synthetic<br/>Deliveries] --> B[Feature Engineering<br/>OneHot + StandardScaler<br/>+ Cyclical hour]
    B --> C[Train/Test Split<br/>80/20]
    C --> D1[Linear Regression]
    C --> D2[Random Forest]
    C --> D3[Gradient Boosting]
    C --> D4[XGBoost]
    C --> D5[LightGBM]
    C --> D6[CatBoost]
    
    D1 --> E[Metrics: MAE, RMSE, R², CV-R²]
    D2 --> E
    D3 --> E
    D4 --> E
    D5 --> E
    D6 --> E
    
    E --> F[Rank by R²]
    F --> G[Optuna Tune Top-K]
    G --> H[Best Model: CatBoost<br/>R²=0.9883, MAE=15.89L]
    H --> I[Persist Pipeline<br/>best_model.joblib]
    
    style A fill:#1e293b,stroke:#22c55e,color:#fff
    style H fill:#1e293b,stroke:#a855f7,color:#fff
    style I fill:#1e293b,stroke:#f59e0b,color:#fff
```

## Docker Deployment Topology

```mermaid
flowchart TB
    subgraph Host[Docker Host]
        subgraph Compose[docker-compose]
            FE_C[frontend container<br/>nginx :80→:3000]
            BE_C[backend container<br/>uvicorn :8000]
            DB_C[db container<br/>PostgreSQL :5432]
        end
        VOL[(pgdata volume)]
    end
    
    User([User Browser]) -->|http://localhost:3000| FE_C
    FE_C -->|/api/* proxy| BE_C
    BE_C -->|SQL| DB_C
    DB_C --> VOL
    
    style Host fill:#0f172a,stroke:#334155,color:#e2e8f0
    style Compose fill:#1e293b,stroke:#22c55e,color:#e2e8f0
```
