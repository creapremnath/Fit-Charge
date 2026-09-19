import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlalchemy import text
from app.core.database import engine, Base
from app.api.v1.user import models as user_models
from app.api.v1.workout import models as workout_models
from app.api.v1.food import models as food_models


def run_migrations():
    print("Connecting to database and applying safe schema updates...")
    
    with engine.connect() as conn:
        with conn.begin():
            # 1. Update user table
            print("Migrating 'user' table...")
            conn.execute(text("ALTER TABLE \"user\" ADD COLUMN IF NOT EXISTS date_of_birth TIMESTAMP;"))
            conn.execute(text("ALTER TABLE \"user\" ADD COLUMN IF NOT EXISTS is_details_completed BOOLEAN DEFAULT FALSE;"))

            # 2. Update user_log table
            print("Migrating 'user_log' table...")
            conn.execute(text("ALTER TABLE \"user_log\" ADD COLUMN IF NOT EXISTS body_fat_pct FLOAT;"))
            conn.execute(text("ALTER TABLE \"user_log\" ADD COLUMN IF NOT EXISTS thighs_cm FLOAT;"))
            conn.execute(text("ALTER TABLE \"user_log\" ADD COLUMN IF NOT EXISTS calves_cm FLOAT;"))
            conn.execute(text("ALTER TABLE \"user_log\" ADD COLUMN IF NOT EXISTS shoulders_cm FLOAT;"))
            conn.execute(text("ALTER TABLE \"user_log\" ADD COLUMN IF NOT EXISTS notes TEXT;"))
            conn.execute(text("ALTER TABLE \"user_log\" ADD COLUMN IF NOT EXISTS log_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP;"))

            # 3. Update workout_log table
            print("Migrating 'workout_log' table...")
            conn.execute(text("ALTER TABLE \"workout_log\" ADD COLUMN IF NOT EXISTS template_id INTEGER;"))
            conn.execute(text("ALTER TABLE \"workout_log\" ADD COLUMN IF NOT EXISTS workout_name VARCHAR;"))
            conn.execute(text("ALTER TABLE \"workout_log\" ADD COLUMN IF NOT EXISTS duration_minutes INTEGER;"))
            conn.execute(text("ALTER TABLE \"workout_log\" ADD COLUMN IF NOT EXISTS notes TEXT;"))
            conn.execute(text("ALTER TABLE \"workout_log\" ALTER COLUMN workout_id DROP NOT NULL;"))

            # 4. Update workout_log_detail table
            print("Migrating 'workout_log_detail' table...")
            conn.execute(text("ALTER TABLE \"workout_log_detail\" ADD COLUMN IF NOT EXISTS workout_id INTEGER;"))
            conn.execute(text("ALTER TABLE \"workout_log_detail\" ADD COLUMN IF NOT EXISTS exercise_name VARCHAR;"))
            conn.execute(text("ALTER TABLE \"workout_log_detail\" ADD COLUMN IF NOT EXISTS set_number INTEGER DEFAULT 1;"))
            conn.execute(text("ALTER TABLE \"workout_log_detail\" ADD COLUMN IF NOT EXISTS set_type VARCHAR DEFAULT 'normal';"))
            conn.execute(text("ALTER TABLE \"workout_log_detail\" ADD COLUMN IF NOT EXISTS reps INTEGER;"))
            conn.execute(text("ALTER TABLE \"workout_log_detail\" ADD COLUMN IF NOT EXISTS weight FLOAT;"))
            conn.execute(text("ALTER TABLE \"workout_log_detail\" ADD COLUMN IF NOT EXISTS tut INTEGER;"))
            conn.execute(text("ALTER TABLE \"workout_log_detail\" ADD COLUMN IF NOT EXISTS rest INTEGER;"))
            conn.execute(text("ALTER TABLE \"workout_log_detail\" ADD COLUMN IF NOT EXISTS rpe FLOAT;"))
            conn.execute(text("ALTER TABLE \"workout_log_detail\" ADD COLUMN IF NOT EXISTS is_completed BOOLEAN DEFAULT TRUE;"))
            conn.execute(text("ALTER TABLE \"workout_log_detail\" ALTER COLUMN detail DROP NOT NULL;"))

    # 5. Create all new tables using SQLAlchemy Base.metadata
    print("Creating any missing tables (user_settings, workout_template, food_item, food_log, meal_template, etc.)...")
    Base.metadata.create_all(bind=engine)
    print("All migrations and tables successfully applied!")


if __name__ == "__main__":
    run_migrations()
