import os
from dotenv import load_dotenv


load_dotenv()


class Config:
    DEBUG = os.getenv("DEBUG", "true").lower() in ("1", "true", "yes")
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
    # Placeholder for database URI or other configs
    SQLALCHEMY_DATABASE_URI = os.getenv("DB_URI", "sqlite:///:memory:")

