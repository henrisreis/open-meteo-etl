import os
import sys

from pathlib import Path
from dotenv import load_dotenv

PROJECT_DIR = Path(__file__).parent.resolve()
env_path = PROJECT_DIR / "config" / ".env"

sys.path.append(str(PROJECT_DIR / "src"))

from open_meteo_etl.extract import DataExtractor
from open_meteo_etl.transform import DataTransformer
from open_meteo_etl.load import DataLoader
from open_meteo_etl.pipeline import ETLPipeline

load_dotenv(env_path)

connection_params = {
    "host": os.getenv("POSTGRES_HOST"),
    "port": os.getenv("POSTGRES_PORT"),
    "dbname": os.getenv("POSTGRES_DB"),
    "user": os.getenv("POSTGRES_USER"),
    "password": os.getenv("POSTGRES_PASSWORD"),
}

extractor = DataExtractor(latitude=-15.7939, longitude=-47.8828)

transformer = DataTransformer()

loader = DataLoader(connection_params=connection_params)

pipeline = ETLPipeline(extractor=extractor, transformer=transformer, loader=loader)

pipeline.run()
