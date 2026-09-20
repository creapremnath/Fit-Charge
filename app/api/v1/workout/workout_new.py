from typing import List, Optional, Union
from fastapi import APIRouter, Depends, Query, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import or_, func, select, ARRAY, String, cast
from sqlalchemy.exc import SQLAlchemyError

from app.core.database import get_session
from app.core.config import settings
from app.core.fc_logger import get_logger
from app.auth.oauth2 import get_current_user
from app.api.v1.authentication.schemas import TokenData
from .models import WorkoutNew
from .schemas import (
    WorkoutNewItem,
    WorkoutNewListResponse,
    WorkoutFilterOptionsResponse,
)

logger = get_logger("fitcharge.workout_new")

router = APIRouter()


def build_cloudinary_media_url(filename: Optional[str]) -> Optional[str]:
    """
    Constructs a direct Cloudinary delivery URL for an image or animated gif asset.
    """
    if not filename:
        return None
    if filename.startswith("http://") or filename.startswith("https://"):
        return filename
    
    cloud_name = settings.cloudinary_cloud_name or "dctazvnjx"
    return f"https://res.cloudinary.com/{cloud_name}/image/upload/{filename.strip()}"


def serialize_workout_new(item: WorkoutNew) -> WorkoutNewItem:
    """
    Converts a WorkoutNew model instance into a WorkoutNewItem schema with computed Cloudinary URLs.
    """
    return WorkoutNewItem(
        id=item.id,
        exercise_id=item.exercise_id,
        name=item.name,
        body_part=item.body_part,
        equipment=item.equipment,
        target_muscle=item.target_muscle,
        main_muscle=item.main_muscle,
        secondary_muscles=item.secondary_muscles or [],
        steps=item.steps or [],
        image=item.image,
        gif=item.gif,
        image_url=build_cloudinary_media_url(item.image),
        gif_url=build_cloudinary_media_url(item.gif),
        is_active=item.is_active,
        created_at=item.created_at,
        updated_at=item.updated_at,
    )


@router.get(
    "/New_workouts_list",
    response_model=WorkoutNewListResponse,
    summary="Get filtered list of workouts from workouts_new table",
)
@router.get(
    "/new_workouts_list",
    response_model=WorkoutNewListResponse,
    include_in_schema=False,
)
@router.get(
    "/new-workouts-list",
    response_model=WorkoutNewListResponse,
    include_in_schema=False,
)
def get_new_workouts_list(
    search: Optional[str] = Query(None, description="Search term matching workout name"),
    name: Optional[List[str]] = Query(None, description="Workout name list or substring filter"),
    body_part: Optional[List[str]] = Query(None, description="Filter by body part (e.g. waist, chest, back, upper legs)"),
    equipment: Optional[List[str]] = Query(None, description="Filter by equipment (e.g. body weight, dumbbell, barbell, cable)"),
    target_muscle: Optional[List[str]] = Query(None, description="Filter by target muscle (e.g. abs, glutes, quads)"),
    main_muscle: Optional[List[str]] = Query(None, description="Filter by main muscle"),
    secondary_muscle: Optional[List[str]] = Query(None, description="Filter by secondary muscle (matches secondary_muscles array)"),
    is_active: Optional[bool] = Query(True, description="Filter active/inactive exercises"),
    limit: int = Query(20, ge=1, le=200, description="Pagination page size"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    session: Session = Depends(get_session),
    current_user: TokenData = Depends(get_current_user),
):
    """
    Fetch paginated and filtered list of exercises from `workouts_new` table with full Cloudinary media URLs.
    """
    try:
        query = session.query(WorkoutNew)

        if is_active is not None:
            query = query.filter(WorkoutNew.is_active == is_active)

        # Keyword search on name
        if search and search.strip():
            clean_search = search.strip().lower()
            query = query.filter(func.lower(WorkoutNew.name).ilike(f"%{clean_search}%"))

        # Explicit name filters
        if name:
            name_filters = [n.strip().lower() for n in name if n.strip()]
            if name_filters:
                query = query.filter(
                    or_(*[func.lower(WorkoutNew.name).ilike(f"%{n}%") for n in name_filters])
                )

        # Body part filter
        if body_part:
            bp_filters = [bp.strip().lower() for bp in body_part if bp.strip()]
            if bp_filters:
                query = query.filter(
                    or_(*[func.lower(WorkoutNew.body_part) == bp for bp in bp_filters])
                )

        # Equipment filter
        if equipment:
            eq_filters = [eq.strip().lower() for eq in equipment if eq.strip()]
            if eq_filters:
                query = query.filter(
                    or_(*[func.lower(WorkoutNew.equipment) == eq for eq in eq_filters])
                )

        # Target muscle filter
        if target_muscle:
            tm_filters = [tm.strip().lower() for tm in target_muscle if tm.strip()]
            if tm_filters:
                query = query.filter(
                    or_(*[func.lower(WorkoutNew.target_muscle) == tm for tm in tm_filters])
                )

        # Main muscle filter
        if main_muscle:
            mm_filters = [mm.strip().lower() for mm in main_muscle if mm.strip()]
            if mm_filters:
                query = query.filter(
                    or_(*[func.lower(WorkoutNew.main_muscle) == mm for mm in mm_filters])
                )

        # Secondary muscle array overlap filter
        if secondary_muscle:
            sm_filters = [sm.strip().lower() for sm in secondary_muscle if sm.strip()]
            if sm_filters:
                query = query.filter(
                    WorkoutNew.secondary_muscles.op("&&")(cast(sm_filters, ARRAY(String)))
                )

        total = query.count()
        results = (
            query.order_by(WorkoutNew.id.asc())
            .offset(offset)
            .limit(limit)
            .all()
        )

        workouts_data = [serialize_workout_new(item) for item in results]

        return WorkoutNewListResponse(
            status_code=200,
            status_message="success",
            message="Workouts fetched successfully",
            total=total,
            limit=limit,
            offset=offset,
            workouts=workouts_data,
        )

    except SQLAlchemyError:
        logger.exception("Error executing New_workouts_list query")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database query error while retrieving workouts list.",
        )


@router.get(
    "/New_workouts_list/filters",
    response_model=WorkoutFilterOptionsResponse,
    summary="Get distinct filter categories (body parts, equipments, muscles)",
)
@router.get(
    "/new_workouts_list/filters",
    response_model=WorkoutFilterOptionsResponse,
    include_in_schema=False,
)
def get_workout_filters(
    session: Session = Depends(get_session),
    current_user: TokenData = Depends(get_current_user),
):
    """
    Returns unique body parts, equipments, target muscles, and main muscles for UI filter selection.
    """
    try:
        body_parts = [
            r[0] for r in session.query(func.distinct(WorkoutNew.body_part))
            .filter(WorkoutNew.body_part.isnot(None), WorkoutNew.is_active == True)
            .order_by(WorkoutNew.body_part.asc())
            .all() if r[0]
        ]

        equipments = [
            r[0] for r in session.query(func.distinct(WorkoutNew.equipment))
            .filter(WorkoutNew.equipment.isnot(None), WorkoutNew.is_active == True)
            .order_by(WorkoutNew.equipment.asc())
            .all() if r[0]
        ]

        target_muscles = [
            r[0] for r in session.query(func.distinct(WorkoutNew.target_muscle))
            .filter(WorkoutNew.target_muscle.isnot(None), WorkoutNew.is_active == True)
            .order_by(WorkoutNew.target_muscle.asc())
            .all() if r[0]
        ]

        main_muscles = [
            r[0] for r in session.query(func.distinct(WorkoutNew.main_muscle))
            .filter(WorkoutNew.main_muscle.isnot(None), WorkoutNew.is_active == True)
            .order_by(WorkoutNew.main_muscle.asc())
            .all() if r[0]
        ]

        return WorkoutFilterOptionsResponse(
            status_code=200,
            status_message="success",
            body_parts=body_parts,
            equipments=equipments,
            target_muscles=target_muscles,
            main_muscles=main_muscles,
        )
    except SQLAlchemyError:
        logger.exception("Error querying workout filter options")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error while retrieving workout filters.",
        )


@router.get(
    "/New_workouts_list/{exercise_identifier}",
    response_model=WorkoutNewItem,
    summary="Get single exercise details by ID or exercise_id code (e.g. 0001)",
)
@router.get(
    "/new_workouts_list/{exercise_identifier}",
    response_model=WorkoutNewItem,
    include_in_schema=False,
)
def get_workout_by_id(
    exercise_identifier: str,
    session: Session = Depends(get_session),
    current_user: TokenData = Depends(get_current_user),
):
    """
    Fetch a single workout from `workouts_new` by numeric database ID or string `exercise_id` (e.g., '0001').
    """
    try:
        item = None
        if exercise_identifier.isdigit():
            item = session.query(WorkoutNew).filter(
                or_(
                    WorkoutNew.id == int(exercise_identifier),
                    WorkoutNew.exercise_id == exercise_identifier
                )
            ).first()
        else:
            item = session.query(WorkoutNew).filter(
                WorkoutNew.exercise_id == exercise_identifier
            ).first()

        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Workout exercise '{exercise_identifier}' not found.",
            )

        return serialize_workout_new(item)

    except HTTPException:
        raise
    except SQLAlchemyError:
        logger.exception(f"Error querying workout with identifier {exercise_identifier}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error while retrieving workout detail.",
        )
