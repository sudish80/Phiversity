import os
from pathlib import Path


TEST_ROOT = Path(__file__).resolve().parent / ".tmp"
TEST_ROOT.mkdir(parents=True, exist_ok=True)

DEFAULT_DB_PATH = TEST_ROOT / f"app_test_{os.getpid()}.db"

os.environ.setdefault("SECRET_KEY", "unit-test-secret-key")
os.environ.setdefault("PHIVERSITY_ENV", "development")
os.environ.setdefault("DATABASE_URL", f"sqlite:///{DEFAULT_DB_PATH}")
