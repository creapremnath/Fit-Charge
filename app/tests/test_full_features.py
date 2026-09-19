import pytest
from datetime import datetime, timezone
from app.api.v1.user.models import User, UserSettings, User_log
from app.api.v1.workout.models import WorkoutTemplate, WorkoutTemplateDay, WorkoutTemplateExercise, Workout_Log
from app.api.v1.food.models import FoodItem, Food_Log, MealTemplate, MealTemplateItem
from app.auth.oauth2 import create_access_token


@pytest.fixture
def sample_user(test_db_session):
    user = User(
        user_id=1,
        username="john_doe",
        email="john@example.com",
        is_verified=True,
        is_active=True,
        role=1,
        is_details_completed=False
    )
    test_db_session.add(user)
    test_db_session.commit()
    test_db_session.refresh(user)
    return user


def test_user_settings_api(test_client, sample_user, auth_headers):
    # 1. GET settings (should auto-provision defaults)
    resp = test_client.get("/api/v1/user/settings", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["weight_unit"] == "kg"
    assert data["theme"] == "dark"

    # 2. PATCH settings
    patch_resp = test_client.patch(
        "/api/v1/user/settings",
        json={"weight_unit": "lbs", "theme": "light", "notifications_enabled": False},
        headers=auth_headers
    )
    assert patch_resp.status_code == 200
    updated = patch_resp.json()
    assert updated["weight_unit"] == "lbs"
    assert updated["theme"] == "light"
    assert updated["notifications_enabled"] is False


def test_user_onboard_and_logs(test_client, sample_user, auth_headers):
    # 1. User details should initially show is_details_completed = False
    detail_resp = test_client.get("/api/v1/user/detail", headers=auth_headers)
    assert detail_resp.status_code == 200
    assert detail_resp.json()["data"]["is_details_completed"] is False

    # 2. Call /onboard endpoint
    onboard_payload = {
        "gender": "Male",
        "date_of_birth": "1998-05-15T00:00:00Z",
        "height_cm": 180.5,
        "weight_kg": 78.0,
        "fitness_goal": "Build Muscle",
        "workout_experience": "Intermediate",
        "height_unit": "cm",
        "weight_unit": "kg"
    }
    onboard_resp = test_client.post("/api/v1/user/onboard", json=onboard_payload, headers=auth_headers)
    assert onboard_resp.status_code == 200
    assert onboard_resp.json()["data"]["is_details_completed"] is True

    # 3. Verify user detail updated
    detail_resp2 = test_client.get("/api/v1/user/detail", headers=auth_headers)
    detail_data = detail_resp2.json()["data"]
    assert detail_data["is_details_completed"] is True
    assert detail_data["gender"] == "Male"
    assert detail_data["latest_body_metrics"]["height_cm"] == 180.5
    assert detail_data["latest_body_metrics"]["weight_kg"] == 78.0

    # 4. Add measurement log
    log_resp = test_client.post(
        "/api/v1/user/logs",
        json={"weight_kg": 79.2, "chest_cm": 102.0, "waist_cm": 82.0, "notes": "Week 2 progress"},
        headers=auth_headers
    )
    assert log_resp.status_code == 201
    log_data = log_resp.json()
    assert log_data["weight_kg"] == 79.2

    # 5. Fetch measurement logs history
    history_resp = test_client.get("/api/v1/user/logs", headers=auth_headers)
    assert history_resp.status_code == 200
    assert len(history_resp.json()) >= 2


def test_workout_template_and_logs(test_client, sample_user, auth_headers):
    # 1. Create workout template
    template_payload = {
        "name": "Push Pull Legs Elite",
        "description": "3 day split for hypertrophy",
        "category": "Hypertrophy",
        "difficulty": "Intermediate",
        "days": [
            {
                "day_name": "Day 1 - Push",
                "day_order": 1,
                "is_rest_day": False,
                "exercises": [
                    {
                        "exercise_name": "Incline Dumbbell Press",
                        "sets": 4,
                        "reps": 10,
                        "weight": 32.0,
                        "rest_seconds": 90
                    },
                    {
                        "exercise_name": "Lateral Raises",
                        "sets": 3,
                        "reps": 15,
                        "weight": 12.0,
                        "rest_seconds": 60
                    }
                ]
            }
        ]
    }
    create_resp = test_client.post("/api/v1/workout/templates", json=template_payload, headers=auth_headers)
    assert create_resp.status_code == 201
    t_data = create_resp.json()
    template_id = t_data["id"]
    assert t_data["name"] == "Push Pull Legs Elite"
    assert len(t_data["days"]) == 1
    assert len(t_data["days"][0]["exercises"]) == 2

    # 2. Fetch templates list
    list_resp = test_client.get("/api/v1/workout/templates", headers=auth_headers)
    assert list_resp.status_code == 200
    assert len(list_resp.json()) >= 1

    # 3. Create workout log
    workout_log_payload = {
        "template_id": template_id,
        "workout_name": "Push Day Session",
        "duration_minutes": 55,
        "notes": "Felt energized, good pump",
        "details": [
            {"exercise_name": "Incline Dumbbell Press", "set_number": 1, "reps": 10, "weight": 32.0, "set_type": "normal"},
            {"exercise_name": "Incline Dumbbell Press", "set_number": 2, "reps": 10, "weight": 32.0, "set_type": "normal"},
            {"exercise_name": "Lateral Raises", "set_number": 1, "reps": 15, "weight": 12.0, "set_type": "normal"}
        ]
    }
    log_resp = test_client.post("/api/v1/workout/logs", json=workout_log_payload, headers=auth_headers)
    assert log_resp.status_code == 201
    wlog_data = log_resp.json()
    assert wlog_data["workout_name"] == "Push Day Session"
    assert len(wlog_data["details"]) == 3
    assert wlog_data["volume"] > 0


def test_food_items_logs_and_meal_templates(test_client, sample_user, auth_headers):
    # 1. Create custom food item
    food_payload = {
        "name": "Whey Isolate Protein",
        "brand": "Optimum Nutrition",
        "serving_size": 30.0,
        "serving_unit": "g",
        "calories": 120.0,
        "protein": 24.0,
        "carbs": 2.0,
        "fat": 1.0
    }
    food_resp = test_client.post("/api/v1/food/items", json=food_payload, headers=auth_headers)
    assert food_resp.status_code == 201
    food_data = food_resp.json()
    food_id = food_data["id"]
    assert food_data["name"] == "Whey Isolate Protein"

    # 2. Search food items
    search_resp = test_client.get("/api/v1/food/items?query=Whey", headers=auth_headers)
    assert search_resp.status_code == 200
    assert len(search_resp.json()) >= 1

    # 3. Create food log
    flog_payload = {
        "food_id": food_id,
        "food_name": "Whey Isolate Protein",
        "meal_type": "breakfast",
        "servings": 1.5,
        "calories": 180.0,
        "protein": 36.0,
        "carbs": 3.0,
        "fat": 1.5
    }
    flog_resp = test_client.post("/api/v1/food/logs", json=flog_payload, headers=auth_headers)
    assert flog_resp.status_code == 201
    assert flog_resp.json()["food_name"] == "Whey Isolate Protein"

    # 4. Get daily food summary
    summary_resp = test_client.get("/api/v1/food/logs", headers=auth_headers)
    assert summary_resp.status_code == 200
    summary_data = summary_resp.json()
    assert summary_data["totals"]["total_calories"] >= 180.0
    assert len(summary_data["by_meal"]["breakfast"]) >= 1

    # 5. Create Meal Template
    meal_temp_payload = {
        "name": "Morning Power Oatmeal",
        "description": "Oats with protein and banana",
        "meal_type": "breakfast",
        "items": [
            {
                "food_id": food_id,
                "food_name": "Whey Isolate Protein",
                "serving_size": 30.0,
                "serving_unit": "g",
                "quantity": 1.0,
                "calories": 120.0,
                "protein": 24.0,
                "carbs": 2.0,
                "fat": 1.0
            },
            {
                "food_name": "Rolled Oats",
                "serving_size": 50.0,
                "serving_unit": "g",
                "quantity": 1.0,
                "calories": 190.0,
                "protein": 7.0,
                "carbs": 34.0,
                "fat": 3.0
            }
        ]
    }
    mtemp_resp = test_client.post("/api/v1/food/meal-templates", json=meal_temp_payload, headers=auth_headers)
    assert mtemp_resp.status_code == 201
    mtemp_data = mtemp_resp.json()
    assert mtemp_data["total_calories"] == 310.0
    assert mtemp_data["total_protein"] == 31.0
    template_id = mtemp_data["id"]

    # 6. 1-Click Log Entire Meal Template
    log_temp_resp = test_client.post(f"/api/v1/food/meal-templates/{template_id}/log", headers=auth_headers)
    assert log_temp_resp.status_code == 200
    logged_items = log_temp_resp.json()
    assert len(logged_items) == 2
