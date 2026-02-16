import logging

from app.data_import.config.core import LOGS_DIR


def configure_logging():
    file_handler = logging.FileHandler(LOGS_DIR / "data_import.log")
    stream_handler = logging.StreamHandler()
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[file_handler, stream_handler],
    )
