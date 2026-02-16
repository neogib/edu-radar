import csv
import logging
from pathlib import Path
from typing import cast

from sqlalchemy.orm import selectinload
from sqlmodel import Session, select

from app.data_import.config.core import CSV_DIR
from app.data_import.utils.db.session import DatabaseManagerBase
from app.data_import.utils.geo import normalize_city_name
from app.models.schools import Szkola

logger = logging.getLogger(__name__)


def _school_to_address_row(school: Szkola) -> list[str | int | None]:
    city = normalize_city_name(school.miejscowosc.nazwa)
    return [
        school.id,
        city,
        school.ulica.nazwa if school.ulica else "",
        school.numer_budynku or "",
        school.kod_pocztowy,
    ]


class SchoolAddressExporter(DatabaseManagerBase):
    """
    Export addresses from the database for external processing.

    Iterates over schools in the database and exports their addresses to a CSV file.
    """

    def __init__(self, export_file: str | Path = CSV_DIR / "school_addresses.csv"):
        super().__init__()
        self.export_file: str | Path = export_file

    def export_school_addresses(self, batch_size: int = 1000) -> None:
        """
        Export school addresses to a CSV file.

        The CSV file will contain the following columns:
        - id: School ID
        - wojewodztwo: Voivodeship name
        - powiat: County name
        - gmina: Municipality name
        - miejscowosc: Locality name
        - ulica: Street name (optional)
        - numer_budynku: Building number (optional)
        - kod_pocztowy: Postal code
        """
        session = self._ensure_session()
        last_id = 0
        total_processed = 0

        while True:
            # Fetch schools in batches
            schools = self.get_schools_batch(session, last_id, batch_size)

            if not schools:
                break  # No more schools to process

            logger.info(
                f"⏳ Processing batch {last_id // batch_size + 1}: {len(schools)} schools"
            )
            # Open CSV file for writing
            with open(
                self.export_file, mode="a", encoding="utf-8", newline=""
            ) as csvfile:
                writer = csv.writer(csvfile)

                # Write header
                if total_processed == 0:
                    writer.writerow(
                        [
                            "id",
                            "miejscowosc",
                            "ulica",
                            "numer_domu",
                            "kod_pocztowy",
                        ]
                    )

                # Iterate over schools and write their addresses
                for school in schools:
                    # Write row
                    writer.writerow(_school_to_address_row(school))
                    total_processed += 1

            last_id += batch_size
        logger.info(
            f"✅ Completed exporting school addresses. Total schools processed: {total_processed}"
        )

    def get_schools_batch(
        self, session: Session, last_id: int = 0, batch_size: int = 1000
    ):
        """Fetch schools with ID greater than last_id"""
        schools = session.exec(
            select(Szkola)
            .where(cast(int, Szkola.id) > last_id)
            .order_by(Szkola.id)  # pyright: ignore[reportArgumentType]
            .limit(batch_size)
            .options(
                selectinload(Szkola.miejscowosc),  # pyright: ignore[reportArgumentType]
                selectinload(Szkola.ulica),  # pyright: ignore[reportArgumentType]
            )
        ).all()
        return schools
