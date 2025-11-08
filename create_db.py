import sys
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError
from app.core.config import settings  # adjust import as needed


def create_database():
    db_url = str(settings.DATABASE_URL)

    # Convert async URL to sync URL FIRST
    if db_url.startswith("postgresql+asyncpg://"):
        sync_url = db_url.replace("postgresql+asyncpg://", "postgresql+psycopg2://")
    elif db_url.startswith("postgresql://"):
        # Assume default is asyncpg in your app, but be safe
        sync_url = db_url.replace("postgresql://", "postgresql+psycopg2://")
    else:
        raise ValueError("Only PostgreSQL is supported")

    # Now parse the sync URL
    # if "/postgres" in sync_url:
    #     raise ValueError("Don't use 'postgres' as target DB in DATABASE_URL")

    base_url, db_name = sync_url.rsplit("/", 1)
    db_name = db_name.split("?")[0]  # strip query params
    admin_url = base_url + "/postgres"

    engine = create_engine(admin_url, isolation_level="AUTOCOMMIT")

    try:
        with engine.connect() as conn:
            conn.execute(text(f'CREATE DATABASE "{db_name}"'))
        print(f"✅ Database '{db_name}' created.")
    except OperationalError as e:
        if "already exists" in str(e):
            print(f"ℹ️ Database '{db_name}' already exists.")
        else:
            print(f"❌ Failed: {e}")
            sys.exit(1)
    finally:
        engine.dispose()


if __name__ == "__main__":
    create_database()
