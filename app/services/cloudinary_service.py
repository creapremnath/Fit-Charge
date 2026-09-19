"""
Private License (fitcharge)

Cloudinary Service for profile picture & media uploads.
"""

from datetime import datetime, timezone
import cloudinary
import cloudinary.uploader
from fastapi import HTTPException, status
from app.core.config import settings
from app.core.fc_logger import get_logger

logger = get_logger("fitcharge.cloudinary")

ALLOWED_IMAGE_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
    "image/heic",
    "image/heif",
    "image/gif",
}

MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB


def init_cloudinary():
    """Ensure Cloudinary is configured with credentials from settings."""
    if not (
        settings.cloudinary_cloud_name
        and settings.cloudinary_api_key
        and settings.cloudinary_api_secret
    ):
        logger.warning("Cloudinary credentials are not fully configured in settings.")
        return False

    cloudinary.config(
        cloud_name=settings.cloudinary_cloud_name,
        api_key=settings.cloudinary_api_key,
        api_secret=settings.cloudinary_api_secret,
        secure=True,
    )
    return True


# Initialize on module load
init_cloudinary()


def upload_profile_image(
    file_bytes: bytes,
    content_type: str,
    user_id: int,
    filename: str = "avatar.jpg"
) -> dict:
    """
    Validates, optimizes, and uploads a profile image to Cloudinary.

    Returns:
        dict: {
            "secure_url": str,
            "public_id": str,
            "format": str,
            "bytes": int,
            "width": int,
            "height": int
        }
    """
    if not init_cloudinary():
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Cloudinary service is not configured on the server."
        )

    if not file_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No image data provided for upload."
        )

    if len(file_bytes) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Image size exceeds the maximum allowed limit of {MAX_FILE_SIZE_BYTES // (1024 * 1024)}MB."
        )

    if content_type and content_type.lower() not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported image type: {content_type}. Allowed types: JPEG, PNG, WEBP, HEIC."
        )

    timestamp = int(datetime.now(timezone.utc).timestamp())
    public_id = f"user_{user_id}_{timestamp}"

    try:
        logger.info(f"Uploading profile image for user {user_id} to Cloudinary...")
        upload_result = cloudinary.uploader.upload(
            file_bytes,
            folder="fitcharge/profile_pictures",
            public_id=public_id,
            overwrite=True,
            resource_type="image",
            transformation=[
                {
                    "width": 800,
                    "height": 800,
                    "crop": "limit",
                    "quality": "auto:good",
                    "fetch_format": "auto",
                }
            ],
        )

        secure_url = upload_result.get("secure_url")
        if not secure_url:
            raise ValueError("No secure_url returned by Cloudinary upload.")

        logger.info(f"Successfully uploaded profile image for user {user_id}: {secure_url}")

        return {
            "secure_url": secure_url,
            "public_id": upload_result.get("public_id", public_id),
            "format": upload_result.get("format", "jpg"),
            "bytes": upload_result.get("bytes", len(file_bytes)),
            "width": upload_result.get("width"),
            "height": upload_result.get("height"),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to upload image to Cloudinary for user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload image to Cloudinary: {str(e)}"
        )
