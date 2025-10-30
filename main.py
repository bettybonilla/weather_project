import logging
import sys

from apis.open_meteo.weather_data import get_weather_data

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
    weather_data = get_weather_data("07310")
    if weather_data:
        print(weather_data.latitude)
        print(weather_data.longitude)
        print(weather_data.current.date_time)
        print(weather_data.current.temp)
        print(weather_data.current.rain_probability)
