from sqlalchemy.orm import declarative_base

# Base class for models - shared between async app and sync migrations
Base = declarative_base()