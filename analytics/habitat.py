def calculate(*args):
    if len(args) == 1 and isinstance(args[0], dict):
        weather = args[0]

        score = 100

        temp = weather["temperature"]
        wind = int(weather["wind_speed"].split()[0])
        precip = weather["precipitation_probability"]

        if temp < 65:
            score -= 25

        if wind > 12:
            score -= 20

        if precip > 40:
            score -= 30

        return max(score, 0)

    if len(args) == 3:
        plant, bee, butterfly = [float(value) for value in args]
        return round((plant + bee + butterfly) / 3)

    raise ValueError("Habitat score expects either a weather dict or three numeric ecosystem scores.")
