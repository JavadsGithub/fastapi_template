from sqlalchemy import event, inspect
from datetime import datetime, timezone
import logging
from app.entities.user import User

logger = logging.getLogger(__name__)


@event.listens_for(User, "before_update", propagate=True)
def update_timestamp(mapper, connection, target):
    """
    قبل از UPDATE روی User اجرا می‌شود.
    updated_at فقط وقتی آپدیت می‌شود که فیلدی غیر از last_login تغییر کرده باشد.
    """
    try:
        state = inspect(target)
        changed_fields = {
            attr.key for attr in state.attrs if attr.history.has_changes()
        }

        if not changed_fields:
            return  # هیچ فیلدی تغییر نکرده

        if changed_fields == {"last_login"}:
            # فقط last_login تغییر کرده → updated_at را دست‌نزن
            return

        # در غیر این صورت → updated_at را آپدیت کن
        target.updated_at = datetime.now(timezone.utc)

    except Exception:
        # در حالت خطا (برای اطمینان) updated_at را تنظیم کن
        target.updated_at = datetime.now(timezone.utc)
        logger.exception("Failed to inspect User for before_update")
