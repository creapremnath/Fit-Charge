from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float
from sqlalchemy.orm import declarative_base
from datetime import datetime
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey

Base = declarative_base()

class Workout(Base):
    __tablename__ = "workout"
    __table_args__ = {'extend_existing': True}

    workout_id = Column(Integer, primary_key=True, autoincrement=True)
    workout_name = Column(String, nullable=True)
    workout_description = Column(String, nullable=True)
    primary_muscle = Column(String, nullable = False)
    secondary_muscle = Column(String, nullable = False)
    met = Column(Integer, nullable = False)
    workout_created_at = Column(DateTime, default=datetime.utcnow)
    workout_updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    


class Workout_log(Base):
    __tablename__ = "workout_log"
    __table_args__ = {'extend_existing': True}

    workout_log_id = Column(Integer, primary_key=True, autoincrement=True)
    workout_id = Column(Integer, ForeignKey("workout.workout_id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("user.user_id", ondelete="CASCADE"), nullable=False)
    workout_date = Column(DateTime, nullable=False)
    tut = Column(Integer, nullable=True)
    rest = Column(Integer, nullable=True)
    rpe = Column(String, nullable=True)
    sets = Column(Integer, nullable=False)
    reps = Column(Integer, nullable=False)
    weight = Column(Float, nullable=False)
    volume = Column(Float, nullable=False)
    distance = Column(Float, nullable=True)
    calories = Column(Float, nullable=False)
    workout_type = Column(String, nullable=True)
    is_super_set = Column(Boolean, default=False)
    is_drop_set = Column(Boolean, default=False)
    is_giant_set = Column(Boolean, default=False)
    is_finisher = Column(Boolean, default=False)
    is_warmup = Column(Boolean, default=False)
    is_failure = Column(Boolean, default=False)
    workout_log_created_at = Column(DateTime, default=datetime.utcnow)
    workout_log_updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # workout_logs = relationship(
    #     "Workout_log",
    #     back_populates="user",
    #     cascade="all, delete-orphan"
    # )
