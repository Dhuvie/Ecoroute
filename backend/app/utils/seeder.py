"""
EcoRoute Backend - Database Seeder
==================================

On first startup, seeds the database with a small fleet of demo vehicles
and a handful of pending deliveries so the dashboard isn't empty.

Author : EcoRoute Backend Team
"""

from __future__ import annotations

import logging
import uuid
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from ..core.database import SessionLocal
from ..models.orm import Customer, Delivery, Vehicle

logger = logging.getLogger("ecoroute.seeder")

# --------------------------------------------------------------------------- #
# Demo data
# --------------------------------------------------------------------------- #
DEMO_VEHICLES = [
    # (vehicle_id, type, fuel, mileage, kerb, cap, speed, maint)
    ("V0001", "motorcycle",         "petrol",  50.0,   180,    50, 60, 0.90),
    ("V0002", "van",                "diesel",  12.0,  2200,  1200, 70, 0.82),
    ("V0003", "van",                "electric", 30.0, 2400,  1200, 65, 0.88),
    ("V0004", "mini_truck",         "diesel",   9.5,  3500,  2500, 65, 0.78),
    ("V0005", "mini_truck",         "cng",     10.5,  3600,  2500, 62, 0.75),
    ("V0006", "truck",              "diesel",   5.5,  8000,  8000, 60, 0.70),
    ("V0007", "truck",              "diesel",   5.2,  8200,  8000, 58, 0.68),
    ("V0008", "truck",              "hybrid",   6.8,  8500,  8000, 60, 0.80),
    ("V0009", "semi_truck",         "diesel",   3.2, 15000, 25000, 55, 0.65),
    ("V0010", "semi_truck",         "diesel",   3.0, 15000, 25000, 55, 0.62),
    ("V0011", "refrigerated_truck", "diesel",   4.0,  9000,  6000, 58, 0.60),
    ("V0012", "refrigerated_truck", "electric", 10.0, 9500,  6000, 55, 0.78),
]

# Indian metro hub coordinates
HUBS = [
    ("Mumbai",    19.0760, 72.8777),
    ("Delhi",     28.7041, 77.1025),
    ("Bangalore", 12.9716, 77.5946),
    ("Hyderabad", 17.3850, 78.4867),
    ("Chennai",   13.0827, 80.2707),
    ("Pune",      18.5204, 73.8567),
]

DEMO_CUSTOMERS = [
    ("Reliance Retail",  "ops@reliance.example",   "+912223001234", "BKC, Mumbai"),
    ("DMart",            "logistics@dmart.example", "+912224567890", "Andheri, Mumbai"),
    ("BigBasket",        "del@bigbasket.example",   "+918012345678", "Whitefield, Bangalore"),
    ("Flipkart",         "logi@flipkart.example",   "+918023456789", "Koramangala, Bangalore"),
    ("Amazon India",     "india@amazon.example",    "+914012345678", "Gachibowli, Hyderabad"),
]


def _haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    import math
    R = 6371.0
    lat1_r, lat2_r = math.radians(lat1), math.radians(lat2)
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1_r) * math.cos(lat2_r) * math.sin(dlon / 2) ** 2
    return 2 * R * math.asin(math.sqrt(a))


def seed_demo_data() -> None:
    """Insert demo vehicles, customers, and pending deliveries if DB is empty."""
    db: Session = SessionLocal()
    try:
        if db.query(Vehicle).count() == 0:
            logger.info("Seeding demo vehicles ...")
            for v in DEMO_VEHICLES:
                db.add(
                    Vehicle(
                        vehicle_id=v[0],
                        vehicle_type=v[1],
                        fuel_type=v[2],
                        base_mileage_kmpl=v[3],
                        kerb_weight_kg=v[4],
                        load_capacity_kg=v[5],
                        avg_speed_kmph=v[6],
                        maintenance_score=v[7],
                        is_active=True,
                    )
                )
            db.commit()
            logger.info("Seeded %d vehicles", len(DEMO_VEHICLES))

        if db.query(Customer).count() == 0:
            logger.info("Seeding demo customers ...")
            for c in DEMO_CUSTOMERS:
                # Use hub coords as customer location
                hub = HUBS[DEMO_CUSTOMERS.index(c) % len(HUBS)]
                db.add(
                    Customer(
                        name=c[0],
                        email=c[1],
                        phone=c[2],
                        address=c[3],
                        lat=hub[1],
                        lon=hub[2],
                    )
                )
            db.commit()
            logger.info("Seeded %d customers", len(DEMO_CUSTOMERS))

        if db.query(Delivery).count() == 0:
            logger.info("Seeding demo deliveries ...")
            import random
            rng = random.Random(42)
            customers = db.query(Customer).all()
            for i in range(20):
                o_hub = rng.choice(HUBS)
                d_hub = rng.choice(HUBS)
                while d_hub[0] == o_hub[0]:
                    d_hub = rng.choice(HUBS)
                customer = rng.choice(customers) if customers else None
                dist_km = _haversine_km(o_hub[1], o_hub[2], d_hub[1], d_hub[2]) * 1.3
                db.add(
                    Delivery(
                        delivery_code=f"DEMO{i+1:04d}",
                        customer_id=customer.id if customer else None,
                        origin_lat=o_hub[1],
                        origin_lon=o_hub[2],
                        destination_lat=d_hub[1],
                        destination_lon=d_hub[2],
                        package_weight_kg=rng.uniform(50, 3000),
                        priority=rng.choice(["low", "medium", "high", "critical"]),
                        deadline_at=datetime.utcnow() + timedelta(hours=rng.randint(6, 48)),
                        status="pending",
                        distance_km=round(dist_km, 2),
                        estimated_fuel_l=round(dist_km * 0.06, 2),
                        estimated_co2_kg=round(dist_km * 0.06 * 2.68, 2),
                        estimated_time_h=round(dist_km / 50.0, 2),
                    )
                )
            db.commit()
            logger.info("Seeded 20 demo deliveries")

        # Randomly assign some pending deliveries to vehicles for analytics
        pending = db.query(Delivery).filter(Delivery.status == "pending").all()
        vehicles = db.query(Vehicle).filter(Vehicle.is_active.is_(True)).all()
        if pending and vehicles:
            import random
            rng = random.Random(7)
            for d in pending[:10]:
                v = rng.choice(vehicles)
                d.vehicle_id = v.id
                d.status = "assigned"
            db.commit()
            logger.info("Auto-assigned 10 demo deliveries")
    except Exception as exc:
        db.rollback()
        logger.exception("Seeder failed: %s", exc)
    finally:
        db.close()
