"""NYSE trading calendar helpers — used to skip batches on weekends/holidays."""
from datetime import datetime
from zoneinfo import ZoneInfo


def is_market_open_today(now: datetime | None = None) -> bool:
    """Return False on weekends and NYSE holidays (US/Eastern timezone).

    The ``holidays`` library's NYSE calendar covers federal and market-specific
    closures (Good Friday, Juneteenth, etc). On import failure we conservatively
    return True so that we don't silently skip work when the dep is missing.
    """
    if now is None:
        now = datetime.now(tz=ZoneInfo("US/Eastern"))
    today = now.date()

    if today.weekday() >= 5:  # 5 = Saturday, 6 = Sunday
        return False

    try:
        from holidays.financial import NYSE
    except ImportError:
        return True

    return today not in NYSE(years=today.year)
