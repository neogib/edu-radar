import argparse
import logging

from app.data_import.geo.exporter import SchoolAddressExporter
from app.data_import.geo.importer import SchoolCoordinatesImporter
from app.data_import.geo.location_shifter import SchoolLocationShifter
from app.data_import.utils.logging_config import configure_logging

logger = logging.getLogger(__name__)


def export_addresses():
    """Export school addresses to CSV for geocoding service."""
    logger.info("📍 Exporting school addresses...")
    with SchoolAddressExporter() as address_exporter:
        address_exporter.export_school_addresses()
    logger.info("✅ School addresses exported successfully")


def import_coordinates():
    """Import converted coordinates from geocoding service."""
    logger.info("🌍 Starting importing converted coordinates...")
    with SchoolCoordinatesImporter() as geoupdater:
        geoupdater.update_school_coordinates()
    logger.info("✅ School coordinates updated successfully")


def shift_school_locations():
    """Move data functionality - to be implemented later."""
    logger.info("Starting to shift school locations...")
    with SchoolLocationShifter() as location_shifter:
        schools_shifted = location_shifter.shift_school_locations()
    logger.info(f"✅ Shifted locations for {schools_shifted} schools successfully")


class TransformOptions:
    option: str  # pyright: ignore[reportUninitializedInstanceVariable]


COMMANDS = {
    "export": export_addresses,
    "import": import_coordinates,
    "move": shift_school_locations,
}


def main():
    """Main function to handle command-line arguments and execute appropriate function."""
    configure_logging()

    parser = argparse.ArgumentParser(
        description="Transform script for school data processing"
    )
    _ = parser.add_argument(
        "-o",
        "--option",
        type=str,
        required=True,
        choices=["export", "import", "move"],
        help="Operation to perform: export (addresses), import (coordinates), or move (shift schools to the sidef when the same coordinates)",
    )

    args = TransformOptions()
    _ = parser.parse_args(namespace=args)

    try:
        COMMANDS[args.option]()
    except Exception as e:
        logger.error(f"❌ Error executing {args.option} operation: {e}")


if __name__ == "__main__":
    main()
