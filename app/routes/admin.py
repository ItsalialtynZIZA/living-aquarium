from fastapi import APIRouter, Depends, HTTPException

from app.auth.dependencies import require_site_admin
from app.site_service import get_active_site_by_id
from app.fish_service import (
    get_fishes_by_site,
    deactivate_fish,
    deactivate_all_fishes,
)
from app.websocket_manager import manager


router = APIRouter(
    prefix="/api/admin",
    tags=["admin"],
)


@router.get("/site")
async def get_admin_site(
    user: dict = Depends(require_site_admin),
):
    site_id = user["site_id"]

    site = get_active_site_by_id(site_id)

    if site is None:
        return {
            "status": "error",
            "message": "Площадка не найдена.",
        }

    return {
        "status": "ok",
        "site": site,
    }


@router.get("/fishes")
async def get_admin_fishes(
    user: dict = Depends(require_site_admin),
):
    site_id = user["site_id"]

    fishes = get_fishes_by_site(site_id)

    result = []

    for fish in fishes:
        result.append(
            {
                "id": fish["id"],
                "filename": fish["filename"],
                "url": (
                    f"/fish/{fish['filename']}"
                ),
                "direction": fish["direction"],
                "confidence": fish["confidence"],
                "created_at": fish["created_at"],
            }
        )

    return {
        "status": "ok",
        "site_id": site_id,
        "count": len(result),
        "fishes": result,
    }


@router.post("/fishes/{fish_id}/remove")
async def remove_fish(
    fish_id: int,
    user: dict = Depends(require_site_admin),
):
    site_id = user["site_id"]

    removed = deactivate_fish(
        fish_id=fish_id,
        site_id=site_id,
    )

    if not removed:
        raise HTTPException(
            status_code=404,
            detail="Рыбка не найдена.",
        )

    await manager.broadcast(
        {
            "type": "remove_fish",
            "fish_id": fish_id,
            "site_id": site_id,
        }
    )

    return {
        "status": "ok",
        "message": "Рыбка убрана с экрана.",
        "fish_id": fish_id,
    }

@router.post("/fishes/clear")
async def clear_fishes(
    user: dict = Depends(require_site_admin),
):
    site_id = user["site_id"]

    fish_ids = deactivate_all_fishes(
        site_id=site_id,
    )

    for fish_id in fish_ids:
        await manager.broadcast(
            {
                "type": "remove_fish",
                "fish_id": fish_id,
                "site_id": site_id,
            }
        )

    return {
        "status": "ok",
        "message": "Все рыбки убраны с экрана.",
        "removed_count": len(fish_ids),
        "fish_ids": fish_ids,
    }