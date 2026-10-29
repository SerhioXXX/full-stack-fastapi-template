from typing import Any

from fastapi import APIRouter, Depends
from sqlmodel import col, func, select

from app.api.deps import SessionDep, require_permission
from app.core.rbac import Permission
from app.models import Item, MetricsPublic, User

router = APIRouter(prefix="/metrics", tags=["metrics"])


@router.get(
    "/",
    dependencies=[Depends(require_permission(Permission.METRICS_READ))],
    response_model=MetricsPublic,
)
def read_metrics(session: SessionDep) -> Any:
    """
    Simple metrics / insights stub backed by live counts.
    """
    total_users = session.exec(select(func.count()).select_from(User)).one()
    active_users = session.exec(
        select(func.count()).select_from(User).where(col(User.is_active).is_(True))
    ).one()
    total_items = session.exec(select(func.count()).select_from(Item)).one()
    return MetricsPublic(
        total_users=total_users,
        active_users=active_users,
        total_items=total_items,
    )
