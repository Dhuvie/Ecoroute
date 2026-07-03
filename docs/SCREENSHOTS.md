# EcoRoute Screenshots

The dashboard UI is fully interactive and runs at <http://localhost:5173> after
`npm run dev` (or <http://localhost:3000> after `docker compose up`).

## Capturing Screenshots

After starting the stack, capture the following views for your portfolio:

1. **Dashboard** (`/`) — KPI grid with fuel saved, CO₂ reduced, cost savings,
   vehicle utilization, plus daily fuel / CO₂ time-series charts.

2. **Vehicles** (`/vehicles`) — Fleet catalogue cards with mileage, capacity,
   maintenance score progress bars, fuel-type badges.

3. **Deliveries** (`/deliveries`) — Sortable table with status/priority badges
   and fuel/CO₂ estimate columns.

4. **Route Optimizer** (`/routes`) — Interactive Leaflet map with origin,
   destination, optimized route polyline, algorithm selector (Dijkstra/A*/OR-Tools),
   and result KPI cards.

5. **Fleet Optimizer** (`/fleet`) — Multi-select deliveries + vehicles, run CVRP
   solver, view assignments with per-vehicle routes, fuel, CO₂, time, and
   overall fuel-saved percentage.

6. **Analytics** (`/analytics`) — Period filter (daily/weekly/monthly/all),
   dual-axis fuel-vs-distance trend, daily deliveries bar chart, top-10 vehicle
   utilization grouped bar chart.

7. **ML Model Insights** (`/model`) — Best-model banner (CatBoost R²=0.9883),
   R² / MAE comparison bar charts across all 6 candidate models, full metrics
   table with CV-R² and train time.

## Recommended Capture Tool

Use [Hotjar](https://hotjar.com), [CleanShot X](https://cleanshot.com), or
the built-in browser screenshot tool (Firefox/Chrome DevTools → Cmd/Ctrl+Shift+P
→ "Capture full size screenshot").

## Sample README Snippet

```markdown
### Screenshots

![Dashboard](docs/screenshots/dashboard.png)
![Route Optimizer](docs/screenshots/route-optimizer.png)
![Fleet Optimizer](docs/screenshots/fleet-optimizer.png)
![ML Insights](docs/screenshots/model-insights.png)
```
