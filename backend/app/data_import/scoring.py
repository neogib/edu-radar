import argparse
import logging

from sqlalchemy import update
from sqlmodel import Session

from app.core.database import engine
from app.core.logging import configure_logging
from app.data_import.config.score import ScoreType
from app.data_import.score.ranking_calculator import RankingCalculator
from app.data_import.score.scorer import Scorer
from app.models.schools import Szkola

logger = logging.getLogger(__name__)


def update_scoring() -> None:
    with Session(engine) as session:
        try:
            logger.info("🧹 Resetting all school scores to NULL...")
            _ = session.exec(update(Szkola).values(wynik=None))

            for score_type in ScoreType:
                logger.info(f"📊 Processing {score_type.name} scores...")
                scorer = Scorer(score_type, session=session)
                scorer.calculate_scores(commit=False)

            session.commit()
        except Exception:
            session.rollback()
            logger.exception("❌ Score calculation transaction failed.")
            raise

    logger.info("🎉 Score calculation completed")


def update_ranking() -> None:
    logger.info("📈 Calculating rankings...")
    with RankingCalculator() as ranking_calculator:
        ranking_calculator.calculate_rankings()
    logger.info("🎉 Ranking calculation completed")


class ScoringOptions:
    option: str  # pyright: ignore[reportUninitializedInstanceVariable]


COMMANDS = {
    "score": update_scoring,
    "rank": update_ranking,
}


def main() -> None:
    configure_logging("scoring.log")

    parser = argparse.ArgumentParser(
        description="Scoring script for score and ranking calculations"
    )
    _ = parser.add_argument(
        "-o",
        "--option",
        type=str,
        required=True,
        choices=["score", "rank"],
        help="Operation to perform: score (calculate school score) or rank (calculate rankings)",
    )

    args = ScoringOptions()
    _ = parser.parse_args(namespace=args)

    try:
        logger.info(f"🚀 Starting {args.option} operation...")
        COMMANDS[args.option]()
        logger.info(f"✅ {args.option.capitalize()} operation completed successfully")
    except Exception as e:
        logger.error(f"❌ Error executing {args.option} operation: {e}")


if __name__ == "__main__":
    main()
