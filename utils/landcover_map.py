"""Helpers for rendering annual HLS canopy-cover comparisons using Google Earth Engine.

The original project used a single NLCD raster, but the required comparison workflow
is better expressed as a time-series of HLS surface-reflectance composites. Each year
is shown as a 5-mile by 5-mile analysis window around a supplied point so that canopy
structure can be compared consistently across years.
"""

from __future__ import annotations

import math
from io import BytesIO
from typing import Sequence


def get_dependency_message() -> str:
    """Return guidance for installing the optional GIS dependencies."""
    return (
        "Install geemap and earthengine-api to use the Earth Engine canopy map."
        " Example: pip install geemap earthengine-api"
    )


def build_hls_landcover_comparison(
    center_lon: float = -88.6,
    center_lat: float = 26.4,
    years: Sequence[int] = (2015, 2020, 2026),
    tile_size_miles: float = 5.0,
):
    """Return the metadata used to compare HLS canopy conditions by year.

    The function does not import Earth Engine unless the caller builds the actual map.
    This keeps the logic easy to test while still documenting the exact comparison that
    should be rendered when the optional GIS dependencies are present.
    """
    results = []
    for year in tuple(int(y) for y in years):
        dataset = "NASA/HLS/HLSL30/v002" if year < 2017 else "NASA/HLS/HLSS30/v002"
        date_start = f"{year}-04-25"
        date_end = f"{year}-04-28" if year < 2017 else f"{year}-04-26"
        results.append(
            {
                "year": year,
                "center_lon": center_lon,
                "center_lat": center_lat,
                "dataset": dataset,
                "start_date": date_start,
                "end_date": date_end,
                "tile_size_miles": float(tile_size_miles),
                "region_miles": float(tile_size_miles),
                "window": {
                    "lat_span_miles": float(tile_size_miles),
                    "lon_span_miles": float(tile_size_miles),
                },
            }
        )
    return results


def get_hls_window_bounds(center_lon: float, center_lat: float, tile_size_miles: float):
    """Return the bounding box for a tile centered on a point in decimal degrees."""
    lat_span_deg = tile_size_miles / 69.0
    lon_scale = max(math.cos(math.radians(center_lat)), 1e-6)
    lon_span_deg = tile_size_miles / (69.0 * lon_scale)
    return [
        center_lon - lon_span_deg / 2,
        center_lat - lat_span_deg / 2,
        center_lon + lon_span_deg / 2,
        center_lat + lat_span_deg / 2,
    ]


_ee_initialized = False

def _ensure_ee_initialized():
    """Initialize Earth Engine once per session."""
    global _ee_initialized
    if _ee_initialized:
        return
    
    try:
        import ee
        import os
        
        # Check if already initialized by attempting a simple call
        try:
            ee.data.getInfo()
            print("[EE] Already initialized")
            _ee_initialized = True
            return
        except (Exception,):
            # Not initialized yet, proceed
            print("[EE] Not yet initialized")
            pass
        
        # Only authenticate if credentials file doesn't exist
        credentials_path = os.path.expanduser("~/.config/earthengine/credentials")
        if not os.path.exists(credentials_path):
            print("[EE] Credentials not found, calling Authenticate()...")
            ee.Authenticate()
        else:
            print("[EE] Credentials found, skipping Authenticate()")
        
        # Try to initialize without project first
        try:
            print("[EE] Calling Initialize() without project...")
            ee.Initialize()
            print("[EE] Earth Engine initialized successfully (default project)")
        except Exception as e:
            print(f"[EE] Default initialization failed: {e}, trying with project='biosphereai'...")
            ee.Initialize(project='biosphereai')
            print("[EE] Earth Engine initialized with project='biosphereai'")
        _ee_initialized = True
    except Exception as exc:
        print(f"[EE ERROR] Initialization failed: {exc}")
        raise RuntimeError(f"Failed to initialize Earth Engine: {exc}")

def fetch_hls_comparison_images(
    center_lon: float = -88.6,
    center_lat: float = 26.4,
    years: Sequence[int] = (2015, 2020, 2026),
    tile_size_miles: float = 5.0,
    dimensions: int = 256,
):
    """Return RGB HLS thumbnails for the requested years and location.

    Each image is the actual Earth Engine HLS layer for the corresponding year, clipped to
    a 5-mile box around the requested coordinate. When the optional dependencies are absent,
    the caller should fall back to the synthetic map representation.
    """
    print(f"[HLS] Fetching comparison images for years {years} at ({center_lat}, {center_lon})")
    try:
        import ee
        from PIL import Image
        import requests
    except ImportError as exc:  # pragma: no cover - import guard
        print(f"[HLS ERROR] Dependencies missing: {exc}")
        raise RuntimeError(
            f"Earth Engine dependencies not available: {exc.__class__.__name__}: {exc}. {get_dependency_message()}"
        ) from exc

    # Initialize Earth Engine on first use
    try:
        print("[HLS] Ensuring EE initialized...")
        _ensure_ee_initialized()
        print("[HLS] EE initialization successful")
    except RuntimeError as e:
        print(f"[HLS] EE initialization failed: {e}")
        # If initialization fails, return empty results for fallback rendering
        return [{"year": year, "image": None, "dataset": "unavailable"} for year in years]

    results = []
    for year in tuple(int(y) for y in years):
        spec = next(item for item in build_hls_landcover_comparison(center_lon, center_lat, (year,), tile_size_miles))
        bounds = get_hls_window_bounds(center_lon, center_lat, tile_size_miles)
        region = [[bounds[0], bounds[1]], [bounds[0], bounds[3]], [bounds[2], bounds[3]], [bounds[2], bounds[1]]]

        try:
            print(f"[HLS] Fetching {year} from {spec['dataset']} ({spec['start_date']} to {spec['end_date']})")
            collection = (
                ee.ImageCollection(spec["dataset"])
                .filter(ee.Filter.date(spec["start_date"], spec["end_date"]))
                .filter(ee.Filter.lt("CLOUD_COVERAGE", 30))
            )
            size = collection.size().getInfo()
            print(f"[HLS] Found {size} images for {year}")
            if size == 0:
                print(f"[HLS] No images available for {year}")
                results.append({"year": year, "image": None, "dataset": spec["dataset"]})
                continue

            composite = collection.median().clip(ee.Geometry.Rectangle(bounds))
            rgb = composite.visualize(bands=["vis-red", "vis-green", "vis-blue"], min=0.01, max=0.18)
            print(f"[HLS] Getting thumbnail URL for {year}...")
            url = rgb.getThumbURL({
                "region": region,
                "dimensions": dimensions,
                "format": "png",
                "bands": ["vis-red", "vis-green", "vis-blue"],
                "min": 0.01,
                "max": 0.18,
            })
            print(f"[HLS] Downloading image from {url[:50]}...")
            response = requests.get(url, timeout=60)
            response.raise_for_status()
            image = Image.open(BytesIO(response.content)).convert("RGB")
            print(f"[HLS] Successfully fetched {year} image ({image.size})")
            results.append({"year": year, "image": image, "dataset": spec["dataset"]})
        except Exception as e:
            print(f"[HLS ERROR] {year}: {type(e).__name__}: {e}")
            results.append({"year": year, "image": None, "dataset": spec["dataset"]})

    return results


def build_hls_comparison_map(
    center_lon: float = -88.6,
    center_lat: float = 26.4,
    years: Sequence[int] = (2015, 2020, 2026),
    tile_size_miles: float = 5.0,
    zoom: int = 12,
):
    """Create a geemap with one 5-mile canopy comparison window per selected year."""
    try:
        import ee
        import geemap
    except ImportError as exc:  # pragma: no cover - import guard
        raise RuntimeError(get_dependency_message()) from exc

    # Initialize Earth Engine
    try:
        _ensure_ee_initialized()
    except RuntimeError:
        # If initialization fails, still try to create the map
        pass
    specs = build_hls_landcover_comparison(center_lon, center_lat, years, tile_size_miles)

    m = geemap.Map()
    m.set_center(center_lon, center_lat, zoom)

    for spec in specs:
        dataset_id = spec["dataset"]
        collection = (
            ee.ImageCollection(dataset_id)
            .filter(ee.Filter.date(spec["start_date"], spec["end_date"]))
            .filter(ee.Filter.lt("CLOUD_COVERAGE", 30))
        )

        red_band = "vis-red"
        nir_band = "vis-nir" if "HLSL30" in dataset_id else "vis-swir"

        bounds = get_hls_window_bounds(center_lon, center_lat, tile_size_miles)
        bounds_geom = ee.Geometry.Rectangle(bounds)

        composite = collection.mean().clip(bounds_geom)
        canopy_index = composite.expression(
            "((nir - red) / (nir + red))",
            {"nir": composite.select(nir_band), "red": composite.select(red_band)},
        ).rename("canopy_cover_proxy")

        canopy_visual = canopy_index.visualize(
            min=0.0,
            max=0.8,
            palette=["#d73027", "#f46d43", "#fdae61", "#fee08b", "#d9ef8b", "#66bd63", "#1a9850"],
        )

        m.add_layer(bounds_geom, {"color": "#93c5fd", "fillColor": "00000000"}, f"{spec['year']} 5-mi window", False)
        m.add_layer(canopy_visual, {}, f"{spec['year']} canopy proxy")

    return m


def build_landcover_map(
    center_lon: float = -88.6,
    center_lat: float = 26.4,
    zoom: int = 12,
    years: Sequence[int] = (2015, 2020, 2026),
    tile_size_miles: float = 5.0,
):
    """Create the standard map comparison for a location across multiple years."""
    return build_hls_comparison_map(center_lon, center_lat, years, tile_size_miles, zoom)
