from datetime import datetime, date

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from models.article import Article
from models.sales import Sales


async def get_sales_stats(db: AsyncSession, start_date: datetime, end_date: date):
    result = await db.execute(
        select(
            func.sum(Sales.total_price).label("total_revenue"),
            func.sum(Sales.quantity * Article.cost_price).label("total_cost"),
            (
                func.sum(Sales.total_price)
                - func.sum(Sales.quantity * Article.cost_price)
            ).label("total_profit"),
            func.count(Sales.id).label("sales_count"),
        )
        .join(Article, Sales.good_id == Article.id)
        .where(Sales.sales_date >= start_date)
        .where(Sales.sales_date <= end_date)
    )

    stats = result.one()  # Получаем единственную строку с агрегированными данными

    return {
        "period_start": start_date,
        "period_end": end_date,
        "total_revenue": float(stats.total_revenue),
        "total_cost": float(stats.total_cost),
        "total_profit": float(stats.total_profit),
        "sales_count": stats.sales_count,
        "profit_margin": (
            float(stats.total_profit / stats.total_revenue * 100)
            if stats.total_revenue
            else 0
        ),
    }
