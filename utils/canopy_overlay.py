def interpolate_canopy_color(canopy_value):
    value = max(0, min(100, float(canopy_value)))
    low = (217, 249, 157)
    high = (127, 29, 29)
    ratio = value / 100.0
    red = int(low[0] + (high[0] - low[0]) * ratio)
    green = int(low[1] + (high[1] - low[1]) * ratio)
    blue = int(low[2] + (high[2] - low[2]) * ratio)
    return f"#{red:02x}{green:02x}{blue:02x}"
