from fastapi import HTTPException, status
from pydantic import PositiveInt
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.charity_project import charity_project_crud
from app.models import CharityProject


async def check_name_duplicate(
    project_name: str,
    session: AsyncSession,
) -> None:
    """Проверить название проекта на уникальность."""
    project_id = await charity_project_crud.get_project_id_by_name(
        project_name, session
    )
    if project_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Проект с таким именем уже существует!',
        )


async def check_charity_project_exists(
    project_id: int,
    session: AsyncSession,
) -> CharityProject:
    """Проверить, что проект существует."""
    charity_project = await charity_project_crud.get_by_attribute(
        'id', project_id, session
    )
    if not charity_project:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail='Проект не найден!'
        )
    return charity_project


async def check_charity_project_invested(project: CharityProject) -> None:
    """Проверить, что в проект внесены средства."""
    if project.invested_amount:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='В проект были внесены средства, не подлежит удалению!',
        )


async def check_if_full_amount_enough(
    full_amount: PositiveInt,
    project_id: int,
    session: AsyncSession,
) -> bool:
    """Проверить, что проект можно обновить и закрыть при необходимости."""
    charity_project = await charity_project_crud.get_by_attribute(
        'id', project_id, session
    )
    if full_amount < charity_project.invested_amount:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail='Сумма проекта не может быть меньше внесённой!',
        )
    return full_amount == charity_project.invested_amount


async def check_charity_project_closed(project: CharityProject) -> None:
    """Проверить, закрыт ли проект."""
    if project.fully_invested:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Закрытый проект нельзя редактировать!',
        )
