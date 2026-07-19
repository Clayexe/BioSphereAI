# Estimate butterfly activity from temperature, wind, and rain conditions.
def calculate(weather):
    score = 100

    temp = weather["temperature"]

    wind = int(
        weather["wind_speed"].split()[0]
    )

    precip = weather["precipitation_probability"]

    if temp < 65:
        score -= 25

    if wind > 12:
        score -= 20

    if precip > 40:
        score -= 30

    return max(score, 0)
