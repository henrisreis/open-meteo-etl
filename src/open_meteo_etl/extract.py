import requests
import logging

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

class DataExtractor:
    def __init__(self, latitude: float, longitude: float):
        self.latitude = latitude
        self.longitude = longitude

    def extract(self) -> dict[str, str]:
        logger.info("\nIniciando a extração dos dados da API...")
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": self.latitude,
            "longitude": self.longitude,
            "current": ("temperature_2m," "relative_humidity_2m," "wind_speed_10m"),
            "timezone": "America/Sao_Paulo",
        }
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        logger.info("\nDados extraídos.")
        return {
            "latitude": data["latitude"],
            "longitude": data["longitude"],
            **data["current"],
        }
