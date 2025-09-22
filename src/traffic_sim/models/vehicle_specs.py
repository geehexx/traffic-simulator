from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class VehicleCatalogEntry:
    type: str
    name: str
    mass_kg: float
    length_m: float
    width_m: float
    # Physics attributes
    power_kw: float
    torque_nm: float
    drag_area_cda: float
    wheelbase_m: float
    tire_friction_mu: float
    brake_efficiency_eta: float


DEFAULT_CATALOG = [
    # Sedans - moderate power, good efficiency
    VehicleCatalogEntry("sedan", "Toyota Camry", 1500, 4.85, 1.85, 150, 250, 0.65, 2.82, 0.8, 0.9),
    VehicleCatalogEntry("sedan", "Honda Accord", 1470, 4.90, 1.86, 140, 240, 0.63, 2.83, 0.8, 0.9),
    VehicleCatalogEntry("sedan", "Ford Fusion", 1600, 4.88, 1.84, 145, 245, 0.67, 2.85, 0.8, 0.9),
    # SUVs - higher power, more drag
    VehicleCatalogEntry("suv", "Ford Explorer", 2050, 5.05, 2.00, 200, 350, 0.85, 3.02, 0.75, 0.85),
    VehicleCatalogEntry(
        "suv", "Toyota Highlander", 1950, 4.95, 1.93, 180, 320, 0.80, 2.95, 0.75, 0.85
    ),
    VehicleCatalogEntry("suv", "Honda CR-V", 1650, 4.70, 1.85, 160, 280, 0.75, 2.70, 0.8, 0.9),
    # Trucks/Vans - high torque, high drag
    VehicleCatalogEntry(
        "truck_van", "Ford F-150", 2300, 5.80, 2.03, 250, 450, 1.10, 3.70, 0.7, 0.8
    ),
    VehicleCatalogEntry(
        "truck_van", "Chevrolet Silverado 1500", 2250, 5.85, 2.03, 240, 440, 1.12, 3.75, 0.7, 0.8
    ),
    VehicleCatalogEntry("truck_van", "Ram 1500", 2350, 5.90, 2.05, 260, 460, 1.15, 3.80, 0.7, 0.8),
    # Motorcycles - high power-to-weight, low drag
    VehicleCatalogEntry(
        "motorbike", "Harley-Davidson Sportster", 230, 2.20, 0.80, 45, 80, 0.35, 1.50, 0.9, 0.95
    ),
    VehicleCatalogEntry(
        "motorbike", "Yamaha YZF-R6", 190, 2.05, 0.70, 90, 65, 0.25, 1.40, 0.9, 0.95
    ),
    VehicleCatalogEntry(
        "motorbike", "Honda CBR600RR", 195, 2.05, 0.70, 85, 63, 0.24, 1.38, 0.9, 0.95
    ),
    # Buses - very high torque, very high drag
    VehicleCatalogEntry(
        "bus", "Blue Bird All American", 12000, 10.7, 2.50, 300, 1200, 3.50, 6.50, 0.6, 0.7
    ),
    VehicleCatalogEntry(
        "bus", "Thomas Saf-T-Liner", 12500, 10.7, 2.50, 310, 1250, 3.60, 6.55, 0.6, 0.7
    ),
    VehicleCatalogEntry("bus", "IC Bus CE", 11800, 10.6, 2.50, 290, 1150, 3.40, 6.45, 0.6, 0.7),
    # Vans - moderate power, high drag
    VehicleCatalogEntry("van", "Ford Transit", 3000, 5.98, 2.05, 180, 400, 1.20, 3.75, 0.7, 0.8),
    VehicleCatalogEntry(
        "van", "Mercedes-Benz Sprinter", 3200, 5.93, 2.02, 190, 420, 1.15, 3.70, 0.7, 0.8
    ),
    VehicleCatalogEntry("van", "Ram ProMaster", 3100, 5.94, 2.01, 185, 410, 1.18, 3.72, 0.7, 0.8),
]
