# BiosphereAI

BiosphereAI is a Python-based ecological dashboard that combines live weather data with habitat-health scoring and AI-guided recommendations. It helps users explore environmental conditions, evaluate habitat quality, and receive actionable ideas for improving plant, pollinator, butterfly, and canopy cover outcomes.

## Features

- Live weather lookup by ZIP code or map selection
- Habitat, plant, bee, butterfly, and canopy cover scoring
- AI assistant recommendations tailored to weather conditions and user goals
- Responsive desktop UI built with Tkinter
- Modular analytics and service layers for easy extension

## Project structure

- app.py — desktop application entry point
- ai/ — recommendation assistant logic
- analytics/ — scoring modules for habitat and ecosystem health
- api/ — weather and geocoding integrations
- services/ — higher-level service orchestration
- tests/ — regression tests for analytics and assistant behavior

## Requirements

Install the dependencies with:

```bash
pip install -r requirements.txt
```

You may also need to install Tkinter support for your Python environment if it is not already present.

## Configuration

The app uses environment-based configuration for external services. Create a local .env file in the project root if needed and add any required API settings.

## Running the app

From the project directory, run:

```bash
python app.py
```

## Example workflow

1. Enter a ZIP code or click the map.
2. Review the live weather and ecosystem metric cards.
3. Enter a prompt such as "improve water retention and shade".
4. Click Generate advice to receive AI-based habitat improvement suggestions.

## Testing

Run the test suite with:

```bash
python -m pytest -q
```

## Notes

BiosphereAI is intended as a practical prototype for environmental monitoring and habitat planning. It can be extended with richer datasets, additional ecological metrics, and more advanced AI integrations.
