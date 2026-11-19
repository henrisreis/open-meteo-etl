import logging
import pandas as pd

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

class DataTransformer:
    def transform(self, data: dict[str, str | int | float]) -> pd.DataFrame:
        logger.info("\nIniciando transformação de dados...")
        df = pd.DataFrame([data])
        df = df.rename(
            columns={
                "time": "data_hora",
                "temperature_2m": "temperatura",
                "relative_humidity_2m": "umidade",
                "wind_speed_10m": "velocidade_vento",
            }
        )
        df["data_hora"] = pd.to_datetime(df["data_hora"])
        logger.info("\nTransformação de dados concluída.")
        return df
