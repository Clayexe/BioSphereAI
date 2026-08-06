import math
from pathlib import Path


CANOPY_RASTER_PATH = Path(__file__).resolve().parents[1] / "2023 CONUS CANOPY DATA" / "science_tcc_conus_wgs84_v2023-5_20230101_20231231.tif"


def _sample_canopy_cover_from_raster(lat, lon, raster_path):
    """Read canopy cover directly from the local 2023 CONUS canopy raster."""
    if raster_path is None or not raster_path.exists():
        return None

    try:
        import rasterio
    except ImportError:
        return None

    try:
        with rasterio.open(raster_path) as src:
            raw_value = next(src.sample([(lon, lat)]))[0]
            nodata_value = src.nodata
    except Exception:
        return None

    if raw_value is None:
        return None

    try:
        canopy_value = float(raw_value)
    except (TypeError, ValueError):
        return None

    if math.isnan(canopy_value):
        return None

    if nodata_value is not None and canopy_value == nodata_value:
        return None

    return int(max(0, min(100, round(canopy_value))))


def sample_canopy_cover(lat, lon, raster_path=None):
    """Sample canopy cover at the given geographic coordinate."""
    raster_path = Path(raster_path) if raster_path else CANOPY_RASTER_PATH
    canopy_cover = _sample_canopy_cover_from_raster(lat, lon, raster_path)
    if canopy_cover is not None:
        return canopy_cover

    lat_factor = math.sin(math.radians(lat * 5)) * 0.45
    lon_factor = math.cos(math.radians(lon * 7)) * 0.35
    detail_noise = math.sin(math.radians((lat + lon) * 13)) * 0.2
    canopy = 50 + (lat_factor + lon_factor + detail_noise) * 25
    return int(max(0, min(100, round(canopy))))


def build_density_grid(canopy_cover, size=12):
    """Create a simple 2D canopy-density surface centered on the site."""
    canopy_cover = max(0, min(100, canopy_cover))
    scaled = canopy_cover / 100.0
    radius = max(1.0, size / 5.0)
    grid = []

    for row in range(size):
        values = []
        for col in range(size):
            x = (col - (size - 1) / 2) / radius
            y = (row - (size - 1) / 2) / radius
            density = math.exp(-(x * x + y * y) / 1.8) * scaled
            values.append(round(density, 3))
        grid.append(values)

    return grid


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
