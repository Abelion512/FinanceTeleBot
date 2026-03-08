import sqlite3
import psycopg2
from loguru import logger
from src.config import settings

class Database:
    def __init__(self):
        self.use_postgres = settings.DATABASE_URL.startswith("postgresql")
        if not self.use_postgres:
            self.conn = sqlite3.connect("market_data.db", check_same_thread=False)
        else:
            self.conn = psycopg2.connect(settings.DATABASE_URL)
        self._init_db()

    def _init_db(self):
        query_sqlite = """
            CREATE TABLE IF NOT EXISTS analysis_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                gold_price REAL,
                ihsg_point REAL,
                sentiment TEXT,
                recommendation TEXT,
                raw_json TEXT
            )
        """
        query_postgres = """
            CREATE TABLE IF NOT EXISTS analysis_history (
                id SERIAL PRIMARY KEY,
                timestamp TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
                gold_price DECIMAL(15, 2),
                ihsg_point DECIMAL(15, 2),
                sentiment TEXT,
                recommendation TEXT,
                raw_json JSONB
            )
        """
        query = query_postgres if self.use_postgres else query_sqlite

        try:
            if self.use_postgres:
                with self.conn.cursor() as cur:
                    cur.execute(query)
                self.conn.commit()
            else:
                with self.conn:
                    self.conn.execute(query)
            logger.info("Database initialized successfully")
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")

    def save_analysis(self, analysis):
        try:
            if self.use_postgres:
                with self.conn.cursor() as cur:
                    cur.execute(
                        "INSERT INTO analysis_history (gold_price, ihsg_point, sentiment, recommendation, raw_json) VALUES (%s, %s, %s, %s, %s)",
                        (analysis.gold_price, analysis.ihsg_point, analysis.sentiment, analysis.recommendation, analysis.model_dump_json())
                    )
                self.conn.commit()
            else:
                with self.conn:
                    self.conn.execute(
                        "INSERT INTO analysis_history (gold_price, ihsg_point, sentiment, recommendation, raw_json) VALUES (?, ?, ?, ?, ?)",
                        (analysis.gold_price, analysis.ihsg_point, analysis.sentiment, analysis.recommendation, analysis.model_dump_json())
                    )
            logger.info("Analysis saved to database")
        except Exception as e:
            logger.error(f"Failed to save analysis: {e}")

    def get_latest_price(self):
        try:
            if self.use_postgres:
                with self.conn.cursor() as cur:
                    cur.execute("SELECT gold_price, ihsg_point, timestamp FROM analysis_history ORDER BY timestamp DESC LIMIT 1")
                    return cur.fetchone()
            else:
                cursor = self.conn.cursor()
                cursor.execute("SELECT gold_price, ihsg_point, timestamp FROM analysis_history ORDER BY timestamp DESC LIMIT 1")
                return cursor.fetchone()
        except Exception as e:
            logger.error(f"Failed to fetch latest price: {e}")
            return None

db = Database()
