import argparse
import logging
import sys

from src.data_import.geo.exporter import SchoolAddressExporter
from src.data_import.geo.importer import SchoolCoordinatesImporter
from src.data_import.main import configure_logging

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


def move_data():
    """Move data functionality - to be implemented later."""
    logger.warning("⚠️ Move functionality is not yet implemented")
    logger.info("🚧 This feature will be added in a future update")


class TransformOptions:
    option: str  # pyright: ignore[reportUninitializedInstanceVariable]


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
        print(args)
        print(type(args))
        if args.option == "export":
            export_addresses()
        elif args.option == "import":
            import_coordinates()
        elif args.option == "move":
            move_data()
    except Exception as e:
        logger.error(f"❌ Error executing {args.option} operation: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
