import pytest
from app.api.v1.workout.workout_new import build_cloudinary_media_url, serialize_workout_new
from app.api.v1.workout.models import WorkoutNew


def test_build_cloudinary_media_url():
    # Empty / None
    assert build_cloudinary_media_url(None) is None
    assert build_cloudinary_media_url("") is None

    # Full HTTP URL
    assert build_cloudinary_media_url("https://example.com/img.jpg") == "https://example.com/img.jpg"

    # Cloudinary filename
    url = build_cloudinary_media_url("0001-2gPfomN.jpg")
    assert "https://res.cloudinary.com/" in url
    assert "0001-2gPfomN.jpg" in url

    gif_url = build_cloudinary_media_url("0001-2gPfomN_gif.gif")
    assert "https://res.cloudinary.com/" in gif_url
    assert "0001-2gPfomN_gif.gif" in gif_url


def test_serialize_workout_new():
    item = WorkoutNew(
        id=1,
        exercise_id="0001",
        name="3/4 sit-up",
        body_part="waist",
        equipment="body weight",
        target_muscle="abs",
        main_muscle="hip flexors",
        secondary_muscles=["hip flexors", "lower back"],
        steps=["Step 1", "Step 2"],
        image="0001-2gPfomN.jpg",
        gif="0001-2gPfomN_gif.gif",
        is_active=True,
    )

    schema = serialize_workout_new(item)
    assert schema.id == 1
    assert schema.exercise_id == "0001"
    assert schema.name == "3/4 sit-up"
    assert schema.body_part == "waist"
    assert schema.target_muscle == "abs"
    assert schema.secondary_muscles == ["hip flexors", "lower back"]
    assert schema.steps == ["Step 1", "Step 2"]
    assert "0001-2gPfomN.jpg" in schema.image_url
    assert "0001-2gPfomN_gif.gif" in schema.gif_url


def test_get_new_workouts_list_empty(test_client, auth_headers):
    response = test_client.get("/api/v1/workout/New_workouts_list", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["status_code"] == 200
    assert data["total"] == 0
    assert data["workouts"] == []


def test_get_new_workouts_list_with_data(test_client, test_db_session, auth_headers):
    workout = WorkoutNew(
        id=1,
        exercise_id="0001",
        name="3/4 sit-up",
        body_part="waist",
        equipment="body weight",
        target_muscle="abs",
        main_muscle="hip flexors",
        secondary_muscles=["hip flexors", "lower back"],
        steps=["Step 1", "Step 2"],
        image="0001-2gPfomN.jpg",
        gif="0001-2gPfomN_gif.gif",
        is_active=True,
    )
    test_db_session.add(workout)
    test_db_session.commit()

    # Default list
    response = test_client.get("/api/v1/workout/New_workouts_list", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["workouts"][0]["name"] == "3/4 sit-up"
    assert data["workouts"][0]["image_url"].endswith("0001-2gPfomN.jpg")
    assert data["workouts"][0]["gif_url"].endswith("0001-2gPfomN_gif.gif")

    # Search filter
    search_res = test_client.get("/api/v1/workout/New_workouts_list?search=sit-up", headers=auth_headers)
    assert search_res.status_code == 200
    assert search_res.json()["total"] == 1

    # Filters endpoint
    filter_res = test_client.get("/api/v1/workout/New_workouts_list/filters", headers=auth_headers)
    assert filter_res.status_code == 200
    filter_data = filter_res.json()
    assert "waist" in filter_data["body_parts"]
    assert "body weight" in filter_data["equipments"]

    # Single exercise detail
    single_res = test_client.get("/api/v1/workout/New_workouts_list/0001", headers=auth_headers)
    assert single_res.status_code == 200
    assert single_res.json()["name"] == "3/4 sit-up"

