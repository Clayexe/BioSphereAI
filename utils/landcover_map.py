"""Helpers for rendering a canopy-cover map using Google Earth Engine.

This module uses the NLCD Tree Canopy Cover image for canopy-focused mapping.
"""

from __future__ import annotations


def get_dependency_message() -> str:
    """Return guidance for installing the optional GIS dependencies."""
    return (
        "Install geemap and earthengine-api to use the Earth Engine canopy map."
        " Example: pip install geemap earthengine-api"
    )


def build_landcover_map(center_lon: float = -88.6, center_lat: float = 26.4, zoom: int = 3):
    """Create an Earth Engine canopy-cover map when optional packages are installed.

    The map uses the NLCD Tree Canopy Cover product so the visualization is
    directly aligned with canopy cover rather than general land-cover classes.
    """
    try:
        import ee
        import geemap
    except ImportError as exc:  # pragma: no cover - import guard
        raise RuntimeError(get_dependency_message()) from exc

    ee.Initialize()

    dataset = ee.Image("USGS/NLCD_RELEASES/2019_REL/NLCD2019_TCC")
    canopy = dataset.select("tree_canopy_cover")

    m = geemap.Map()
    m.set_center(center_lon, center_lat, zoom)
    m.add_layer(canopy, {"min": 0, "max": 100, "palette": ["#f7fbff", "#deebf7", "#c6dbef", "#9ecae1", "#6baed6", "#3182bd", "#08519c"]}, "Tree Canopy Cover")
    return m
