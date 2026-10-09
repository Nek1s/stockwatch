from fastapi import APIRouter

from app.api.deps import CurrentUser, DbSession
from app.models.user import User
from app.schemas.auth import TelegramSettingsRequest, UserResponse

router = APIRouter(prefix="/api/v1/notifications", tags=["notifications"])


@router.put("/telegram", response_model=UserResponse)
def configure_telegram(
    payload: TelegramSettingsRequest, current_user: CurrentUser, db: DbSession
) -> User:
    """Store the current user's destination chat without exposing bot credentials."""
    current_user.telegram_chat_id = payload.telegram_chat_id
    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    return current_user
