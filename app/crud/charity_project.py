from typing import Dict, List, Optional, Union

from fastapi.encoders import jsonable_encoder
from sqlalchemy import func, select, true
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models import CharityProject
from app.schemas.charity_project import CharityProjectUpdate


class CRUDCharityProject(CRUDBase):
    async def get_project_id_by_name(
        self,
        project_name: str,
        session: AsyncSession,
    ) -> Optional[int]:
        db_project_id = await session.execute(
            select(CharityProject.id).where(
                CharityProject.name == project_name
            )
        )
        db_project_id = db_project_id.scalars().first()
        return db_project_id

    async def update(
        self,
        db_project: CharityProject,
        project_in: CharityProjectUpdate,
        session: AsyncSession,
    ) -> CharityProject:
        obj_data = jsonable_encoder(db_project)
        update_data = project_in.dict(exclude_unset=True)

        for field in obj_data:
            if field in update_data:
                setattr(db_project, field, update_data[field])
        session.add(db_project)
        await session.commit()
        await session.refresh(db_project)
        return db_project

    async def remove(
        self,
        db_project: CharityProject,
        session: AsyncSession,
    ) -> CharityProject:
        await session.delete(db_project)
        await session.commit()
        return db_project

    async def get_projects_by_completion_rate(
        self,
        session: AsyncSession,
    ) -> List[Dict[str, Union[float, str]]]:
        projects = await session.execute(
            select(
                [
                    CharityProject.name,
                    (
                        func.julianday(CharityProject.close_date) -
                        func.julianday(CharityProject.create_date)
                    ).label('completion'),
                    CharityProject.description
                ]
            ).where(
                CharityProject.fully_invested == true()
            ).order_by('completion')
        )
        projects = projects.all()
        return projects


charity_project_crud = CRUDCharityProject(CharityProject)
