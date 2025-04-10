from pydantic import BaseModel


class PermissionResponse(BaseModel):
    user_id: int
    message: str
