import argparse
import logging

from src.data_import.api.db.decomposer import Decomposer
from src.data_import.api.exceptions import SchoolsDataError
from src.data_import.api.fetcher import SchoolsAPIFetcher
from src.data_import.config.api import APISettings
from src.data_import.config.excel import ExamType
from src.data_import.excel.db.table_splitter import TableSplitter
from src.data_import.excel.reader import ExcelReader
from src.data_import.utils.logging_config import configure_logging

logger = logging.getLogger(__name__)


def print_error_message(segment_number: int, current_page: int):
    logger.error(f"""
                 ❌ Error processing segment {segment_number}
                 ⚠️ Process stopped at page {current_page}
                 💡 You can resume the process by starting from this page""")


def api_importer():
    api_fetcher = SchoolsAPIFetcher()
    current_page = APISettings.START_PAGE
    total_processed = 0
    segment_number = 1

    while True:
        try:
            logger.info(
                f"🔄 Processing segment {segment_number} (starting from page {current_page})..."
            )
            schools_data, next_page = api_fetcher.fetch_schools_segment(
                start_page=current_page
            )

            if not schools_data:
                logger.info("ℹ️ No more schools to process")  # noqa: RUF001
                break

            logger.info(
                f"⚡ Processing {len(schools_data)} schools from segment {segment_number}..."
            )
            with Decomposer() as decomposer:
                decomposer.prune_and_decompose_schools(schools_data)

            total_processed += len(schools_data)
            logger.info(
                f"✅ Successfully processed segment {segment_number} ({len(schools_data)} schools)"
            )
            logger.info(f"📊 Total schools processed so far: {total_processed}")

            if not next_page:
                logger.info("🏁 No more pages to process")
                break

            current_page = next_page
            segment_number += 1

        except SchoolsDataError as e:
            logger.error(f"📛 Schools data error: {e}")
            print_error_message(segment_number, current_page)
            break

        except Exception as e:
            logger.critical(f"🚨 Unhandled, critical error: {e}")
            print_error_message(segment_number, current_page)
            break

    logger.info(
        f"🎉 Import from API completed. Total schools processed: {total_processed}"
    )


def excel_importer():
    reader = ExcelReader()
    logger.info("📄 Starting Excel data import...")
    for exam_type in ExamType:
        logger.info(f"📊 Processing {exam_type.name} exam data...")
        for year, exam_data in reader.load_files(exam_type):
            logger.info(f"🗓️ Processing {exam_type.name} data for year {year}...")
            with TableSplitter(exam_data, exam_type, year) as splitter:
                if not splitter.initialize():
                    logger.warning(
                        f"⚠️ Skipping invalid {exam_type.name} data for year {year}"
                    )
                    continue  # skip this file - it was invalid
                splitter.split_exam_results()
                logger.info(
                    f"✅ Successfully processed {exam_type.name} data for year {year}"
                )
    logger.info("🎉 Excel data import completed")


class ImportOptions:
    option: str  # pyright: ignore[reportUninitializedInstanceVariable]


COMMANDS = {
    "api": api_importer,
    "excel": excel_importer,
}


def main():
    configure_logging()

    parser = argparse.ArgumentParser(
        description="Main import script for school data processing"
    )
    _ = parser.add_argument(
        "-o",
        "--option",
        type=str,
        required=True,
        choices=["api", "excel"],
        help="Operation to perform: api (schools API import) or excel (exam data import)",
    )

    args = ImportOptions()
    _ = parser.parse_args(namespace=args)

    try:
        logger.info(f"🚀 Starting {args.option} operation...")
        COMMANDS[args.option]()
        logger.info(f"✅ {args.option.capitalize()} operation completed successfully")
    except Exception as e:
        logger.error(f"❌ Error executing {args.option} operation: {e}")


if __name__ == "__main__":
    main()
