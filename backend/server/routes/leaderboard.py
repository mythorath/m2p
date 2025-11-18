"""Leaderboard API routes."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel

from database import get_db
from server.leaderboard import get_leaderboard_manager, LeaderboardManager


router = APIRouter(prefix="/api/leaderboard", tags=["leaderboard"])


# Pydantic models
class LeaderboardEntry(BaseModel):
    """Leaderboard entry response model."""
    rank: int
    previous_rank: Optional[int]
    rank_change: str
    user_id: int
    wallet_address: str
    wallet_truncated: str
    display_name: Optional[str]
    is_verified: bool
    total_mined_advc: float
    total_ap: int
    period_score: float
    last_mining_event: Optional[str]

    class Config:
        from_attributes = True


class PlayerRankResponse(BaseModel):
    """Player rank response model."""
    player_rank: int
    previous_rank: Optional[int]
    rank_change: str
    period_score: float
    nearby_rankings: List[LeaderboardEntry]


class LeaderboardResponse(BaseModel):
    """Leaderboard response model."""
    period: str
    total_entries: int
    limit: int
    offset: int
    entries: List[LeaderboardEntry]


@router.get("/periods", response_model=List[str])
async def get_periods():
    """Get available leaderboard periods."""
    return LeaderboardManager.PERIODS


@router.get("/{period}", response_model=LeaderboardResponse)
async def get_leaderboard(
    period: str,
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    use_cache: bool = Query(default=True),
    db: Session = Depends(get_db)
):
    """Get leaderboard for a specific period.

    Args:
        period: Leaderboard period (all_time, this_week, today, efficiency)
        limit: Number of entries to return (1-500)
        offset: Offset for pagination
        use_cache: Whether to use cached data
        db: Database session

    Returns:
        Leaderboard data
    """
    manager = get_leaderboard_manager(db)

    try:
        entries = manager.get_leaderboard(period, limit, offset, use_cache)

        return LeaderboardResponse(
            period=period,
            total_entries=len(entries),
            limit=limit,
            offset=offset,
            entries=entries
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{period}/player/{wallet_address}", response_model=PlayerRankResponse)
async def get_player_rank(
    period: str,
    wallet_address: str,
    context: int = Query(default=5, ge=0, le=20),
    db: Session = Depends(get_db)
):
    """Get player's rank and nearby rankings.

    Args:
        period: Leaderboard period
        wallet_address: Player's wallet address
        context: Number of positions to show above and below
        db: Database session

    Returns:
        Player rank data with nearby rankings
    """
    manager = get_leaderboard_manager(db)

    try:
        result = manager.get_player_rank(wallet_address, period, context)

        if result is None:
            raise HTTPException(
                status_code=404,
                detail=f"Player not found in top {manager.top_limit} for period {period}"
            )

        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{period}/refresh")
async def refresh_leaderboard(
    period: str,
    db: Session = Depends(get_db)
):
    """Manually refresh leaderboard cache for a period.

    Args:
        period: Leaderboard period to refresh
        db: Database session

    Returns:
        Update status
    """
    manager = get_leaderboard_manager(db)

    try:
        update_counts = manager.update_leaderboard_cache(period)

        return {
            "status": "success",
            "period": period,
            "entries_updated": update_counts.get(period, 0)
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/refresh-all")
async def refresh_all_leaderboards(db: Session = Depends(get_db)):
    """Manually refresh all leaderboard caches.

    Args:
        db: Database session

    Returns:
        Update status for all periods
    """
    manager = get_leaderboard_manager(db)
    update_counts = manager.update_leaderboard_cache()

    return {
        "status": "success",
        "updates": update_counts
    }
