"""
Tests for Cloudinary upload service and profile pic upload endpoint.
"""

import pytest
from unittest.mock import patch, MagicMock
from app.api.v1.user.models import User
from app.auth.utils import encrypt_password
from app.services.cloudinary_service import upload_profile_image


class TestCloudinaryService:
    """Unit tests for Cloudinary upload service."""

    @patch("cloudinary.uploader.upload")
    @patch("app.services.cloudinary_service.init_cloudinary", return_value=True)
    def test_upload_profile_image_success(self, mock_init, mock_upload):
        mock_upload.return_value = {
            "secure_url": "https://res.cloudinary.com/fitcharge/image/upload/v1234/test.jpg",
            "public_id": "fitcharge/profile_pictures/user_1_123456",
            "format": "jpg",
            "bytes": 5000,
            "width": 800,
            "height": 800,
        }

        sample_bytes = b"test-image-binary-data"
        result = upload_profile_image(
            file_bytes=sample_bytes,
            content_type="image/jpeg",
            user_id=1,
            filename="my_photo.jpg"
        )

        assert result["secure_url"] == "https://res.cloudinary.com/fitcharge/image/upload/v1234/test.jpg"
        assert result["public_id"] == "fitcharge/profile_pictures/user_1_123456"
        assert mock_upload.called

    def test_upload_profile_image_invalid_type(self):
        sample_bytes = b"test-text-data"
        with pytest.raises(Exception) as exc_info:
            upload_profile_image(
                file_bytes=sample_bytes,
                content_type="text/plain",
                user_id=1
            )
        assert "Unsupported image type" in str(exc_info.value.detail)

    def test_upload_profile_image_empty_bytes(self):
        with pytest.raises(Exception) as exc_info:
            upload_profile_image(
                file_bytes=b"",
                content_type="image/png",
                user_id=1
            )
        assert "No image data provided" in str(exc_info.value.detail)
