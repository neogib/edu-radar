import csv
import logging
from pathlib import Path

from src.app.models.schools import Szkola
from src.data_import.core.config import CSV_DIR
from src.data_import.utils.db.session import DatabaseManagerBase

logger = logging.getLogger(__name__)


class SchoolCoordinatesImporter(DatabaseManagerBase):
    def __init__(
        self, converted_file: str | Path = CSV_DIR / "converted_addresses.csv"
    ):
        super().__init__()
        self.converted_file: str | Path = converted_file

    def update_school_coordinates(self) -> None:
        """
        Updates school geolocation data based on the CSV file.
        """
        session = self._ensure_session()
        total_processed = 0
        total_skipped = 0

        # Define required columns
        col_id = "id"
        col_lat = "g_szer"
        col_lon = "g_dlug"

        try:
            with open(self.converted_file, encoding="utf-8") as csvfile:
                # Use DictReader to automatically handle headers
                reader = csv.DictReader(csvfile)

                # Validate headers exist
                if not reader.fieldnames or not {col_id, col_lat, col_lon}.issubset(
                    reader.fieldnames
                ):
                    logger.critical(
                        f"🚨 Critical error: Missing required headers in CSV. Expected: {col_id}, {col_lat}, {col_lon}"
                    )
                    return

                for row in reader:
                    logger.debug(f"Processing row: {row}")

                    # 1. Validate data presence
                    raw_id = row.get(col_id, "").strip()
                    raw_lat = row.get(col_lat, "").strip()
                    raw_lon = row.get(col_lon, "").strip()

                    if not raw_id or not raw_lat or not raw_lon:
                        total_skipped += 1
                        logger.warning(
                            f"Skipping row with missing data: ID={raw_id},  Lat={raw_lat}, Lon={raw_lon}"
                        )
                        continue

                    # 2. Find School
                    try:
                        school_id = int(raw_id)
                        school = session.get(Szkola, school_id)
                    except ValueError:
                        logger.error(f"Invalid ID format: {raw_id}")
                        continue

                    if not school:
                        logger.warning(f"School with ID {school_id} not found.")
                        continue

                    # 3. Update Data
                    try:
                        school.geolokalizacja_latitude = float(raw_lat)
                        school.geolokalizacja_longitude = float(raw_lon)
                        session.add(school)
                        total_processed += 1

                        # Commit every 100 records to avoid large transactions
                        if total_processed % 100 == 0:
                            session.commit()

                    except ValueError:
                        logger.error(f"Invalid coordinate format for ID {school_id}")
                        continue

                # Final commit for remaining records
                session.commit()
                logger.info(
                    f"Successfully updated coordinates for {total_processed} schools."
                )
                logger.info(
                    f"Skipped {total_skipped} rows due to missing or invalid data."
                )

        except FileNotFoundError:
            logger.critical(f"File not found: {self.converted_file}")
        except Exception as e:
            session.rollback()
            logger.critical(f"Unexpected error during import: {e}")
            raise
