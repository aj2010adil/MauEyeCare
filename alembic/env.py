from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Alembic Config object
config = context.config
fileConfig(config.config_file_name)

# Set DB URL from .env
db_url = os.getenv("DATABASE_URL")
if not db_url:
    raise ValueError("DATABASE_URL not found in environment. Make sure .env file is present.")

config.set_main_option('sqlalchemy.url', db_url)

# If you have SQLAlchemy models, import them here
target_metadata = None

