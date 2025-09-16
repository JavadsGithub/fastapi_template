from sqlalchemy.orm import declarative_base

Base = declarative_base()

# Import all models here so that Alembic can detect them when autogenerating migrations:
# from app.models import item  # noqa: F401
