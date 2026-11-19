import logging
import psycopg2
import pandas as pd

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

class DataLoader:
    def __init__(self, connection_params: dict[str, str | int]) -> None:
        self.connection_params = connection_params

    def load(self, df: pd.DataFrame) -> None:
        logger.info("\nIniciando carga de dados...")
        create_table = """
            CREATE TABLE IF NOT EXISTS dados_clima(
                data_hora TIMESTAMP,
                latitude DECIMAL(10, 8),
                longitude DECIMAL(11, 8),
                temperatura DECIMAL(5, 2),
                umidade DECIMAL(5, 2),
                velocidade_vento DECIMAL(6, 2)
            );
        """

        insert_data = """
            INSERT INTO dados_clima (
                data_hora,
                latitude,
                longitude,
                temperatura,
                umidade,
                velocidade_vento
            )
            VALUES (
                %(data_hora)s,
                %(latitude)s,
                %(longitude)s,
                %(temperatura)s,
                %(umidade)s,
                %(velocidade_vento)s
            );
        """

        records = df.to_dict(orient="records")

        with psycopg2.connect(**self.connection_params) as conn:
            with conn.cursor() as cur:
                cur.execute(create_table)
                cur.executemany(insert_data, records)
                
        logger.info("\nCarga de dados concluída.")
