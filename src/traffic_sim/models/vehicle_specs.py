from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class VehicleCatalogEntry:
    type: str
    name: str
    mass_kg: float
    length_m: float
    width_m: float


DEFAULT_CATALOG = [
    VehicleCatalogEntry("sedan", "Toyota Camry", 1500, 4.85, 1.85),
    VehicleCatalogEntry("sedan", "Honda Accord", 1470, 4.90, 1.86),
    VehicleCatalogEntry("sedan", "Ford Fusion", 1600, 4.88, 1.84),
    VehicleCatalogEntry("suv", "Ford Explorer", 2050, 5.05, 2.00),
    VehicleCatalogEntry("suv", "Toyota Highlander", 1950, 4.95, 1.93),
    VehicleCatalogEntry("suv", "Honda CR-V", 1650, 4.70, 1.85),
    VehicleCatalogEntry("truck_van", "Ford F-150", 2300, 5.80, 2.03),
    VehicleCatalogEntry("truck_van", "Chevrolet Silverado 1500", 2250, 5.85, 2.03),
    VehicleCatalogEntry("truck_van", "Ram 1500", 2350, 5.90, 2.05),
    VehicleCatalogEntry("motorbike", "Harley-Davidson Sportster", 230, 2.20, 0.80),
    VehicleCatalogEntry("motorbike", "Yamaha YZF-R6", 190, 2.05, 0.70),
    VehicleCatalogEntry("motorbike", "Honda CBR600RR", 195, 2.05, 0.70),
    VehicleCatalogEntry("bus", "Blue Bird All American", 12000, 10.7, 2.50),
    VehicleCatalogEntry("bus", "Thomas Saf-T-Liner", 12500, 10.7, 2.50),
    VehicleCatalogEntry("bus", "IC Bus CE", 11800, 10.6, 2.50),
    VehicleCatalogEntry("van", "Ford Transit", 3000, 5.98, 2.05),
    VehicleCatalogEntry("van", "Mercedes-Benz Sprinter", 3200, 5.93, 2.02),
    VehicleCatalogEntry("van", "Ram ProMaster", 3100, 5.94, 2.01),
]


