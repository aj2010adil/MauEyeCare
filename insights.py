from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db_session
from dependencies import get_current_user_id
from visit import Visit
from schemas import SuggestionsResponse


router = APIRouter()


@router.get("/suggestions", response_model=SuggestionsResponse)
async def suggest(db: AsyncSession = Depends(get_db_session), user_id: str = Depends(get_current_user_id)):
    # Simple heuristic insights based on issue frequency
    rows = (await db.execute(select(Visit.issue, func.count().label("c")).group_by(Visit.issue))).all()
    suggestions: list[str] = []
    for issue, count in rows:
        if not issue:
            continue
        if count >= 5:
            suggestions.append(f"High frequency of '{issue}'. Consider a targeted awareness post.")
    if not suggestions:
        suggestions.append("Stable operations. Encourage patients to book follow-up visits via WhatsApp.")
    return {"suggestions": suggestions}
