# weather_project

This repo displays weather data for a specified zip code in the US.

## Features
- Uses the FastAPI Python web framework.
- Integrates 3 weather APIs: [Open-Meteo](https://open-meteo.com/), [NWS](https://www.weather.gov/documentation/services-web-api), [WeatherAPI](https://www.weatherapi.com/docs/).
- Returns a JSON response displaying the following for the current hour:
```json
{
  "avg_temp": 78,
  "avg_rain_prob": 0,
  "unit": "fahrenheit",
  "last_updated": "2026-03-10T20:40:51+00:00"
}
```

## Usage / Getting Started
- After spinning up your FastAPI server, you can run a curl command with the following:
  - Endpoint: /weather-retriever
  - Required query parameter: zip_code
    - Must be a 5-digit zip code in the US.

```bash
curl "localhost:8000/weather-retriever?zip_code=12345" 
```
