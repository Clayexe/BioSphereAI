import math


def sample_canopy_cover(lat, lon):
    """Sample a deterministic canopy cover estimate from latitude/longitude.

    In a real implementation this would read an NLCD tree canopy raster at the
    site coordinate. For this prototype, the function returns a reproducible
    0-100 canopy percentage based on the point location.
    """
    lat_factor = math.sin(math.radians(lat * 5)) * 0.45
    lon_factor = math.cos(math.radians(lon * 7)) * 0.35
    detail_noise = math.sin(math.radians((lat + lon) * 13)) * 0.2
    canopy = 50 + (lat_factor + lon_factor + detail_noise) * 25
    return int(max(0, min(100, round(canopy))))


def calculate_throughfall(canopy_cover, precipitation_probability):
    """Estimate water reaching the ground given canopy interception."""
    rainfall_mm = round((precipitation_probability / 100.0) * 12.0, 1)
    throughfall_mm = round(rainfall_mm * (1 - canopy_cover / 100.0), 1)
    interception_mm = round(rainfall_mm - throughfall_mm, 1)
    return {
        "canopy_cover": canopy_cover,
        "rainfall_mm": rainfall_mm,
        "throughfall_mm": throughfall_mm,
        "interception_loss_mm": interception_mm,
        "throughfall_pct": round((throughfall_mm / rainfall_mm) * 100, 1) if rainfall_mm else 0,
    }
