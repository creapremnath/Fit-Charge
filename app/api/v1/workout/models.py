from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, ForeignKey, UniqueConstraint
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

Base = declarative_base()

class Muscle(Base):
    __tablename__ = "muscle"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)

class Workout(Base):
    __tablename__ = "workout"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=True)
    description = Column(String, nullable=True)
    met = Column(Float, nullable = False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

 
class Workout_Muscle(Base):
    __tablename__ = "workout_muscle"
    __table_args__ = (
        UniqueConstraint("workout_id", "muscle_id", name="uq_workout_muscle"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    workout_id = Column(Integer, ForeignKey("workout.id", ondelete="CASCADE"), nullable = False)
    muscle_id = Column(Integer, ForeignKey("muscle.id", ondelete="CASCADE"), nullable = False)   
    is_primary = Column(Boolean, nullable=True) 
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Workout_Log(Base):
    __tablename__ = "workout_log"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, autoincrement=True)
    workout_id = Column(Integer, ForeignKey("workout.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("user.user_id", ondelete="CASCADE"), nullable=False)
    workout_date = Column(DateTime, nullable=False)
    tut = Column(Integer, nullable=True)
    rest = Column(Integer, nullable=True)
    rpe = Column(Float, nullable=True)
    sets = Column(Integer, nullable=False)
    reps = Column(Integer, nullable=False)
    weight = Column(Float, nullable=False)
    volume = Column(Float, nullable=False)
    distance = Column(Float, nullable=True)
    # workout_type = Column(String, nullable=True) (covered in workout_log_detail table)
    # is_super_set = Column(Boolean, default=False)
    # is_drop_set = Column(Boolean, default=False)
    # is_giant_set = Column(Boolean, default=False)
    # is_finisher = Column(Boolean, default=False)
    # is_warmup = Column(Boolean, default=False)
    # is_failure = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # workout_logs = relationship(
    #     "Workout_log",
    #     back_populates="user",
    #     cascade="all, delete-orphan"
    # )

class Workout_Log_Detail(Base):
    __tablename__ = "workout_log_detail"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, autoincrement=True)
    workout_log_id = Column(Integer, ForeignKey("workout_log.id", ondelete="CASCADE"), nullable = False)
    detail = Column(String, nullable = False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
