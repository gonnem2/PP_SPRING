from datetime import datetime

from pydantic import BaseModel


class SalesStatsResponse(BaseModel):
    period_start: datetime
    period_end: datetime
    total_revenue: float
    total_cost: float
    total_profit: float
    sales_count: int
    profit_margin: float
