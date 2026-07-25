# Estimate canopy cover impact on habitat resilience from weather and site density.
def calculate(weather, canopy_cover=None):
    score = 100

    if canopy_cover is None:
        canopy_cover = 50

    canopy_cover = max(0, min(100, float(canopy_cover)))

    temp = weather.get("temperature", 70)
    precip = weather.get("precipitation_probability", 30)

    if canopy_cover < 20:
        score -= 35
    elif canopy_cover < 45:
        score -= 18
    elif canopy_cover > 75:
        score += 4

    if temp > 90:
        score -= 8
    elif temp < 45:
        score -= 6

    if precip > 60:
        score -= 8

    return max(min(round(score), 100), 0)
