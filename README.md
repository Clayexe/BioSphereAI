# BiosphereAI

BiosphereAI is a Python desktop dashboard for exploring ecosystem health with live weather, canopy modeling, and habitat scoring. It combines weather fetches, geocoding, and ecological analytics to present plant, pollinator, butterfly, habitat, and canopy metrics in a Tkinter interface.

## Features

- Live weather lookup by ZIP code or latitude/longitude
- Plant, bee, butterfly, habitat, and canopy health scoring
- Canopy density visualization with throughfall and interception estimates
- Desktop dashboard built with Tkinter and Matplotlib
- Modular backend layers for analytics, weather integration, and scheduled updates

## Project structure

- `app.py` — desktop dashboard entry point
- `analytics/` — ecosystem scoring modules
- `api/` — geocoding and weather API integrations
- `config/` — environment and app settings
- `database/` — database helpers, schema, and repository code
- `scheduler/` — scheduled updater hooks
- `services/` — orchestration layer for weather and canopy services
- `tests/` — automated regression tests
- `utils/` — shared helper utilities

## Requirements

Install dependencies with:

```bash
pip install -r requirements.txt
```

> Note: Make sure your Python installation includes Tkinter support, as the desktop UI depends on it.

## Configuration

The app loads environment settings via `python-dotenv`. Create a `.env` file in the project root if you need to override defaults such as API configuration, database path, or logging settings.

## Running the app

From the project directory, run:

```bash
python app.py
```

## Testing

Run the test suite with:

```bash
python -m pytest -q
```

## Notes

BiosphereAI is designed to be extended with additional environmental data sources, richer ecological analytics, and scheduler-driven refresh workflows. The current codebase focuses on a lightweight desktop visualization experience with live weather and canopy-informed scoring.
