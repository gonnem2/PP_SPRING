from sqlalchemy.ext.asyncio import AsyncSession

from models.receipt import Receipt


async def create_receipt(current_user: dict, db: AsyncSession):
    new_receipt = Receipt(user_id=current_user["id"])
    db.add(new_receipt)
    await db.commit()
    await db.refresh(new_receipt)
    return new_receipt
