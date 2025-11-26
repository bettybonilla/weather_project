import logging
import sys

import apis.open_meteo.weather_data

# Configures the global root logger format
# The StreamHandler class sends the logs to the console
# stdout is typically white (OS contingent)
# stderr is typically red (OS contingent) -> stream parameter default
logging.basicConfig(
    level=logging.DEBUG,
    handlers=[logging.StreamHandler(stream=sys.stdout)],
    format="%(asctime)s | %(levelname)s | %(name)s: Line %(lineno)d | %(message)s",
)

if __name__ == "__main__":
    open_meteo_weather_data = apis.open_meteo.weather_data.get_weather_data("07310")
    if open_meteo_weather_data:
        print(open_meteo_weather_data.latitude)
        print(open_meteo_weather_data.longitude)
        print(open_meteo_weather_data.current.date_time)
        print(open_meteo_weather_data.current.temperature)
        print(open_meteo_weather_data.current.rain_probability)
