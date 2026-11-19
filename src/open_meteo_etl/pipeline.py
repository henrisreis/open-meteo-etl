import logging

from open_meteo_etl.extract import DataExtractor
from open_meteo_etl.transform import DataTransformer
from open_meteo_etl.load import DataLoader

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

class ETLPipeline:
    def __init__(
        self, extractor: DataExtractor, transformer: DataTransformer, loader: DataLoader
    ):
        self.extractor = extractor
        self.transformer = transformer
        self.loader = loader

    def run(self) -> None:
        logger.info("\nIniciando pipeline...")
        # Extract
        raw_data = self.extractor.extract()

        # Transform
        transformed_data = self.transformer.transform(raw_data)

        # Load
        self.loader.load(transformed_data)
        logger.info("\nPipeline concluído.")
