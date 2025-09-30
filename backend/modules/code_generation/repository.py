"""Repository for Code Generation Module."""

from typing import Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from backend.db.models import CodeGenerationSession, GeneratedFile


class CodeGenerationRepository:
    """Repository for code generation sessions."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, gen_session: CodeGenerationSession) -> CodeGenerationSession:
        self.session.add(gen_session)
        await self.session.commit()
        await self.session.refresh(gen_session)
        return gen_session

    async def get_by_id(self, session_id: UUID) -> Optional[CodeGenerationSession]:
        result = await self.session.execute(
            select(CodeGenerationSession)
            .where(CodeGenerationSession.id == session_id)
            .options(selectinload(CodeGenerationSession.generated_files))
        )
        return result.scalar_one_or_none()

    async def get_by_project(self, project_id: UUID) -> list[CodeGenerationSession]:
        result = await self.session.execute(
            select(CodeGenerationSession)
            .where(CodeGenerationSession.project_id == project_id)
            .order_by(CodeGenerationSession.created_at.desc())
        )
        return list(result.scalars().all())

    async def update(self, gen_session: CodeGenerationSession) -> CodeGenerationSession:
        await self.session.commit()
        await self.session.refresh(gen_session)
        return gen_session

    async def delete(self, gen_session: CodeGenerationSession) -> None:
        await self.session.delete(gen_session)
        await self.session.commit()


class GeneratedFileRepository:
    """Repository for generated files."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, file: GeneratedFile) -> GeneratedFile:
        self.session.add(file)
        await self.session.commit()
        await self.session.refresh(file)
        return file

    async def get_by_session(self, session_id: UUID) -> list[GeneratedFile]:
        result = await self.session.execute(
            select(GeneratedFile).where(GeneratedFile.session_id == session_id).order_by(GeneratedFile.file_path)
        )
        return list(result.scalars().all())
