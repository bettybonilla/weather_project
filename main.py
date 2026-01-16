import logging
import sys

import apis.nws.weather_data
import apis.open_meteo.weather_data
import apis.weatherapi.weather_data

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
        print("-----------------------")
        print(open_meteo_weather_data.date_time)
        print(open_meteo_weather_data.temperature)
        print(open_meteo_weather_data.rain_probability)
        print("-----------------------")
    nws_weather_data = apis.nws.weather_data.get_weather_data("07310")
    if nws_weather_data:
        print("-----------------------")
        print(nws_weather_data.date_time)
        print(nws_weather_data.temperature)
        print(nws_weather_data.rain_probability)
    weatherapi_weather_data = apis.weatherapi.weather_data.get_weather_data("07310")
    if weatherapi_weather_data:
        print("-----------------------")
        print("weatherapi_weather_data:")
        print(
            weatherapi_weather_data.date_time, type(weatherapi_weather_data.date_time)
        )
        print(
            weatherapi_weather_data.temperature,
            type(weatherapi_weather_data.temperature),
        )
        print(
            weatherapi_weather_data.rain_probability,
            type(weatherapi_weather_data.rain_probability),
        )
        print("-----------------------")
