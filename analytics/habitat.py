# Blend the ecological scores into a single habitat-health estimate.
def calculate(*args):
    if len(args) == 1 and isinstance(args[0], dict):
        weather = args[0]

        score = 100
        temp = weather["temperature"]
        wind = int(str(weather["wind_speed"]).split()[0])
        precip = weather["precipitation_probability"]
        humidity = weather["humidity"]

        if temp < 60:
            score -= 18
        elif temp > 88:
            score -= 18
        elif 60 <= temp <= 80:
            score += 4

        if wind > 15:
            score -= 22
        elif wind > 10:
            score -= 10

        if precip > 60:
            score -= 24
        elif precip > 40:
            score -= 12
        elif precip < 15:
            score -= 8

        if 35 <= humidity <= 70:
            score += 6
        elif humidity < 25 or humidity > 80:
            score -= 10

        return max(min(round(score), 100), 0)

    if len(args) == 3:
        plant, bee, butterfly = [float(value) for value in args]
        scores = (plant, bee, butterfly)
        average = sum(scores) / 3
        spread = max(scores) - min(scores)

        weighted_score = (plant * 0.40) + (bee * 0.35) + (butterfly * 0.25)
        stability_score = max(0, 100 - (spread * 1.35))

        habitat_score = round((weighted_score * 0.55) + (average * 0.25) + (stability_score * 0.20))
        return max(min(habitat_score, 100), 0)

    raise ValueError("Habitat score expects either a weather dict or three numeric ecosystem scores.")
