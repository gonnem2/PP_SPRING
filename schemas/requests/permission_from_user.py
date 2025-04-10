from pydantic import BaseModel


class PermissionSet(BaseModel):

    set_owner: bool = False
    set_warehouse_worker: bool = False
    set_seller: bool = True
