import streamlit as st

from services.weather_service import WeatherService

from analytics.plant import calculate as plant_score
from analytics.pollinator import calculate as bee_score
from analytics.butterfly import calculate as butterfly_score
from analytics.habitat import calculate as habitat_score

st.set_page_config(page_title="BioSphereAI")

service = WeatherService()

zipcode = st.text_input(
    "ZIP Code",
    value="13760"
)

weather = service.get_by_zip(zipcode)

plant = plant_score(weather)
bee = bee_score(weather)
butterfly = butterfly_score(weather)

habitat = habitat_score(
    plant,
    bee,
    butterfly
)

st.title("🌎 BioSphereAI")

st.subheader(
    f"{weather['city']}, {weather['state']}"
)

c1, c2 = st.columns(2)

with c1:
    st.metric(
        "Temperature",
        f"{weather['temperature']}°F"
    )

    st.metric(
        "Rain Chance",
        f"{weather['precipitation_probability']}%"
    )

with c2:
    st.metric(
        "Wind",
        weather['wind_speed']
    )

    st.metric(
        "Forecast",
        weather['forecast']
    )

st.divider()

st.metric(
    "🌱 Plant Health",
    f"{plant}%"
)

st.metric(
    "🐝 Bee Activity",
    f"{bee}%"
)

st.metric(
    "🦋 Butterfly Activity",
    f"{butterfly}%"
)

st.metric(
    "🌳 Habitat Health",
    f"{habitat}%"
)