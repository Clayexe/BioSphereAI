def calculate(weather):
    score = 100
    temp = weather["temperature"]
    precip = weather["precipitation_probability"]

    if temp > 90:
        score -= 25

    if temp < 45:
        score -= 15
    
    if precip < 10:
        score -= 20

    return max(score,0)