import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg://cdms_user:cdms_pass@localhost:15433/cdms_db")
VIETFUL_BASE_URL = os.getenv("VIETFUL_BASE_URL", "http://localhost:18001")
POLL_ENABLED = os.getenv("POLL_ENABLED", "true") == "true"
POLL_INTERVAL_SECONDS = int(os.getenv("POLL_INTERVAL_SECONDS", "15"))
