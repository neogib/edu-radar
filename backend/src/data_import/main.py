import argparse
import asyncio
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


async def api_importer() -> None:
    total_processed = 0

    for zlikwidowana in (False, True):
        api_fetcher = SchoolsAPIFetcher(zlikwidowana=zlikwidowana)
        segment_number = 1

        status_label = "zlikwidowana=true" if zlikwidowana else "zlikwidowana=false"
        logger.info(f"🔄 Starting import for {status_label}...")

        try:
            batch_iterator = api_fetcher.fetch_schools_batches(
                start_page=APISettings.START_PAGE,
            )
            async for schools_data in batch_iterator:
                logger.info(
                    f"🔄 Processing segment {segment_number} ({status_label})..."
                )
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
                segment_number += 1

        except SchoolsDataError as e:
            logger.error(f"📛 Schools data error: {e}")
            logger.error(
                f"❌ Error processing segment {segment_number} ({status_label})"
            )
            break
        except Exception as e:
            logger.critical(f"🚨 Unhandled, critical error: {e}")
            logger.error(
                f"❌ Error processing segment {segment_number} ({status_label})"
            )
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
    "api": lambda: asyncio.run(api_importer()),
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
