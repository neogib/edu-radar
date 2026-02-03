from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "storage"
CSV_DIR = DATA_DIR / "csv"
LOGS_DIR = DATA_DIR / "logs"
