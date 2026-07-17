def calculate(weather):

    score = 100

    temp = weather["temperature"]

    wind = int(
        weather["wind_speed"].split()[0]
    )

    precip = weather["precipitation_probability"]

    if temp < 60:
        score -= 20

    if temp > 90:
        score -= 25

    if wind > 15:
        score -= 25

    if precip > 60:
        score -= 30

    return max(score, 0)