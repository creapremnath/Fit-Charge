from datetime import datetime, timezone
from sqlalchemy import Column, Integer, BigInteger, String, Boolean, DateTime, Float, ForeignKey, UniqueConstraint, ARRAY, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base


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
    met = Column(Float, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))


class Workout_Muscle(Base):
    __tablename__ = "workout_muscle"
    __table_args__ = (
        UniqueConstraint("workout_id", "muscle_id", name="uq_workout_muscle"),
        {'extend_existing': True},
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    workout_id = Column(Integer, ForeignKey("workout.id", ondelete="CASCADE"), nullable=False)
    muscle_id = Column(Integer, ForeignKey("muscle.id", ondelete="CASCADE"), nullable=False)   
    is_primary_muscle = Column(Boolean, nullable=True) 
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))


class WorkoutTemplate(Base):
    __tablename__ = "workout_template"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("user.user_id", ondelete="CASCADE"), nullable=True) # Null for system/preset templates
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    category = Column(String, nullable=True, default="Hypertrophy") # 'Hypertrophy', 'Strength', 'Endurance', 'Full Body', 'Split'
    difficulty = Column(String, nullable=True, default="Intermediate") # 'Beginner', 'Intermediate', 'Advanced'
    is_custom = Column(Boolean, default=True)
    is_public = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    days = relationship(
        "WorkoutTemplateDay",
        back_populates="template",
        cascade="all, delete-orphan",
        order_by="WorkoutTemplateDay.day_order"
    )


class WorkoutTemplateDay(Base):
    __tablename__ = "workout_template_day"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, autoincrement=True)
    template_id = Column(Integer, ForeignKey("workout_template.id", ondelete="CASCADE"), nullable=False)
    day_name = Column(String, nullable=False) # 'Monday', 'Day 1 - Push', etc.
    day_order = Column(Integer, default=1)
    is_rest_day = Column(Boolean, default=False)

    template = relationship("WorkoutTemplate", back_populates="days")
    exercises = relationship(
        "WorkoutTemplateExercise",
        back_populates="template_day",
        cascade="all, delete-orphan",
        order_by="WorkoutTemplateExercise.order_index"
    )


class WorkoutTemplateExercise(Base):
    __tablename__ = "workout_template_exercise"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, autoincrement=True)
    template_day_id = Column(Integer, ForeignKey("workout_template_day.id", ondelete="CASCADE"), nullable=False)
    workout_id = Column(Integer, ForeignKey("workout.id", ondelete="SET NULL"), nullable=True)
    exercise_name = Column(String, nullable=False)
    sets = Column(Integer, default=3)
    reps = Column(Integer, default=10)
    weight = Column(Float, default=0.0)
    rest_seconds = Column(Integer, default=60) # Rest time in seconds
    order_index = Column(Integer, default=1)
    notes = Column(String, nullable=True)

    template_day = relationship("WorkoutTemplateDay", back_populates="exercises")


class Workout_Log(Base):
    __tablename__ = "workout_log"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, autoincrement=True)
    workout_id = Column(Integer, ForeignKey("workout.id", ondelete="CASCADE"), nullable=True)
    user_id = Column(Integer, ForeignKey("user.user_id", ondelete="CASCADE"), nullable=False)
    template_id = Column(Integer, ForeignKey("workout_template.id", ondelete="SET NULL"), nullable=True)
    workout_name = Column(String, nullable=True)
    workout_date = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    tut = Column(Integer, nullable=True)
    rest = Column(Integer, nullable=True)
    rpe = Column(Float, nullable=True)
    sets = Column(Integer, nullable=True, default=1)
    reps = Column(Integer, nullable=True, default=1)
    weight = Column(Float, nullable=True, default=0.0)
    volume = Column(Float, nullable=True, default=0.0)
    distance = Column(Float, nullable=True)
    duration_minutes = Column(Integer, nullable=True)
    notes = Column(String, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    details = relationship(
        "Workout_Log_Detail",
        back_populates="workout_log",
        cascade="all, delete-orphan"
    )


class Workout_Log_Detail(Base):
    __tablename__ = "workout_log_detail"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, autoincrement=True)
    workout_log_id = Column(Integer, ForeignKey("workout_log.id", ondelete="CASCADE"), nullable=False)
    workout_id = Column(Integer, ForeignKey("workout.id", ondelete="SET NULL"), nullable=True)
    exercise_name = Column(String, nullable=True)
    set_number = Column(Integer, nullable=True, default=1)
    set_type = Column(String, nullable=True, default="normal") # 'normal', 'warmup', 'drop_set', 'failure', 'super_set'
    reps = Column(Integer, nullable=True)
    weight = Column(Float, nullable=True)
    tut = Column(Integer, nullable=True)
    rest = Column(Integer, nullable=True)
    rpe = Column(Float, nullable=True)
    is_completed = Column(Boolean, default=True)
    detail = Column(String, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    workout_log = relationship("Workout_Log", back_populates="details")


class WorkoutNew(Base):
    __tablename__ = "workouts_new"
    __table_args__ = {'extend_existing': True}

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    exercise_id = Column(String, nullable=False, index=True)
    name = Column(String, nullable=False, index=True)
    body_part = Column(String, nullable=True, index=True)
    equipment = Column(String, nullable=True, index=True)
    target_muscle = Column(String, nullable=True, index=True)
    main_muscle = Column(String, nullable=True, index=True)
    secondary_muscles = Column(ARRAY(String).with_variant(JSON, "sqlite"), nullable=True)
    steps = Column(ARRAY(String).with_variant(JSON, "sqlite"), nullable=True)
    image = Column(String, nullable=True)
    gif = Column(String, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

