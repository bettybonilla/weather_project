import os

# Structure of DATABASE_URL when using sqlalchemy:
# mysql+asyncmy://weather_user:weather_password@mysql:3306/weather

mysql_host = os.getenv("MYSQL_HOST", "mysql")
mysql_port = os.getenv("MYSQL_PORT", "3306")
mysql_db = os.getenv("MYSQL_DB", "weather")
mysql_user = os.getenv("MYSQL_USER", "weather_user")
mysql_password = os.getenv("MYSQL_PASSWORD", "weather_password")

DATABASE_URL = f"mysql+asyncmy://{mysql_user}:{mysql_password}@{mysql_host}:{mysql_port}/{mysql_db}"
REQUEST_TIMEOUT = 5
