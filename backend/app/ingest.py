"""Pull live Japan-based jobs from the boards in japan_boards.py, close the
ones that were taken down, and refresh every user's matches (which also
sends new-match notifications).

Usage:
    python -m app.ingest                                  # full run
    python -m app.ingest --board lever:woven-by-toyota    # one board
    python -m app.ingest --board ashby:openai --dry-run   # fetch and print only
    python -m app.ingest --skip-matching                  # jobs only

Meant to run on a schedule (see .github/workflows/ingest-jobs.yml) rather
than inside a web request: a full run makes a few hundred HTTP calls plus
one LLM extraction per new or changed posting.
"""

import argparse
import logging
import sys
import time

from app.core.config import get_settings
from app.database.session import SessionLocal
from app.ingestion.ats_sources import PLATFORMS
from app.ingestion.japan_boards import JAPAN_BOARDS, BoardConfig
from app.ingestion.pipeline import ingest_source
from app.models.enums import JobStatus
from app.models.job import Job
from app.models.user import User
from app.services.match_service import recompute_matches_for_user

logger = logging.getLogger("app.ingest")


def _select_boards(spec: str | None) -> list[BoardConfig]:
    if not spec:
        return JAPAN_BOARDS
    platform, _, slug = spec.partition(":")
    if platform not in PLATFORMS or not slug:
        raise SystemExit(f"--board must look like <platform>:<slug>, platform one of {sorted(PLATFORMS)}")
    known = next((b for b in JAPAN_BOARDS if b.platform == platform and b.slug == slug), None)
    return [known or BoardConfig(platform, slug, company=slug)]


def _adapter(board: BoardConfig):
    return PLATFORMS[board.platform](board.slug, board.company, board.website, board.industry)


def _retire_demo_jobs(db) -> int:
    """Live mode: hide the seeded demo postings rather than delete them, so
    saved jobs and history that reference them keep working."""
    demo_jobs = db.query(Job).filter(Job.is_demo_data.is_(True), Job.status != JobStatus.CLOSED).all()
    for job in demo_jobs:
        job.status = JobStatus.CLOSED
    db.commit()
    return len(demo_jobs)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--board", help="only this board, as <platform>:<slug>")
    parser.add_argument("--dry-run", action="store_true", help="fetch and print postings without saving")
    parser.add_argument("--skip-matching", action="store_true", help="don't recompute matches afterwards")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    logging.getLogger("httpx").setLevel(logging.WARNING)
    boards = _select_boards(args.board)
    started = time.monotonic()

    if args.dry_run:
        for board in boards:
            postings = _adapter(board).fetch_jobs()
            print(f"{board.platform}:{board.slug} -- {len(postings)} Japan postings")
            for posting in postings[:10]:
                print(f"  [{posting.description_language}] {posting.title} | {posting.location} | {posting.work_mode.value}")
        return 0

    db = SessionLocal()
    try:
        if not get_settings().demo_mode:
            retired = _retire_demo_jobs(db)
            if retired:
                logger.info("DEMO_MODE is off: closed %d demo postings", retired)

        failed = []
        for board in boards:
            try:
                jobs = ingest_source(db, _adapter(board), close_missing=True)
                logger.info("%s:%s -- %d open Japan postings", board.platform, board.slug, len(jobs))
            except Exception:
                # One board being down (or renamed) must not stop the rest.
                db.rollback()
                failed.append(f"{board.platform}:{board.slug}")
                logger.exception("Skipped %s:%s", board.platform, board.slug)

        active = db.query(Job).filter(Job.status == JobStatus.ACTIVE).count()
        logger.info("Active jobs after ingestion: %d (%d boards failed: %s)", active, len(failed), ", ".join(failed) or "none")

        if not args.skip_matching:
            users = db.query(User).all()
            for user in users:
                recompute_matches_for_user(db, user, notify=True)
            logger.info("Recomputed matches for %d users", len(users))
    finally:
        db.close()

    logger.info("Done in %.0fs", time.monotonic() - started)
    return 1 if failed and len(failed) == len(boards) else 0


if __name__ == "__main__":
    sys.exit(main())
