from __future__ import annotations


class RecommendationAssistant:
    """Generate simple, score-aware advice for improving habitat performance."""

    def __init__(self):
        self.low_score_threshold = 70

    def recommend(self, weather, scores, user_prompt=None):
        temperature = weather["temperature"]
        wind_speed = int(str(weather["wind_speed"]).split()[0])
        precipitation = weather["precipitation_probability"]
        prompt = (user_prompt or "").strip().lower()

        suggestions = []

        if scores["plant"] < self.low_score_threshold:
            if temperature > 88:
                suggestions.append("Plant health is under pressure from heat. Add shade coverage and increase deep watering to protect roots.")
            elif precipitation < 15:
                suggestions.append("Plant health would benefit from mulch and irrigation to retain soil moisture during dry conditions.")
            else:
                suggestions.append("Introduce more resilient native plants and improve soil coverage to stabilize plant health.")

        if scores["bee"] < self.low_score_threshold:
            if temperature < 60:
                suggestions.append("Bee activity is lower in cool weather. Add more bloom timing diversity and sheltered nectar plants that can still support activity.")
            if wind_speed > 15:
                suggestions.append("High wind is reducing bee movement. Add windbreak planting or more sheltered pollinator areas.")
            if precipitation > 50:
                suggestions.append("Wet conditions are discouraging bee activity. Create drier, protected nectar patches to support pollinators.")
            suggestions.append("Expand pollinator-friendly flowers across the site to boost bee activity and long-term habitat resilience.")

        if scores["butterfly"] < self.low_score_threshold:
            if temperature < 65:
                suggestions.append("Butterflies are less active below ideal temperature ranges. Include more sunny nectar plants and sheltered resting zones.")
            if wind_speed > 12:
                suggestions.append("Wind is disrupting butterfly movement. Add low windbreaks and calmer microhabitats for resting and feeding.")
            if precipitation > 40:
                suggestions.append("Heavy rain is lowering butterfly activity. Add rain-tolerant nectar species and drainage-friendly planting beds.")

        if scores["habitat"] < self.low_score_threshold:
            suggestions.append("Habitat health needs more ecosystem balance. Diversify planting, ensure water access, and give pollinators a broader range of shelter and forage.")

        if prompt:
            prompt_focus = []
            if any(term in prompt for term in ["water", "moisture", "irrigation", "rain"]):
                prompt_focus.append("Prioritize water retention with mulch, rain gardens, or irrigation planning.")
            if any(term in prompt for term in ["canopy", "tree", "trees", "cover"]):
                prompt_focus.append("Increase canopy cover with layered trees and shrubs to improve cooling and habitat structure.")
            if any(term in prompt for term in ["shade", "cool", "heat"]):
                prompt_focus.append("Add shade structures or cooler, heat-tolerant planting zones.")
            if any(term in prompt for term in ["pollinator", "bee", "butterfly"]):
                prompt_focus.append("Expand pollinator-friendly habitat with nectar-rich and host plants.")
            if any(term in prompt for term in ["soil", "nutrient", "fertil"]):
                prompt_focus.append("Improve soil health with compost, cover crops, and native rooting layers.")
            if any(term in prompt for term in ["wind", "shelter", "protect"]):
                prompt_focus.append("Increase sheltering and wind buffering with hedges or low barriers.")

            if prompt_focus:
                suggestions = prompt_focus + suggestions

        if not suggestions:
            suggestions.append("The ecosystem is trending well. Keep the current mix of shade, water access, and pollinator-friendly planting to sustain the score.")

        return suggestions

    def summarize(self, weather, scores, user_prompt=None):
        recommendations = self.recommend(weather, scores, user_prompt=user_prompt)
        return "\n\n".join(f"• {item}" for item in recommendations)
