from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from uuid import UUID
from models.roles import Role
from schemas.roles_schemas import RoleCreate, RoleUpdate
from sqlalchemy.sql import exists

"""
Data Access Layer for user role management: create, retrieve, update, delete, and check roles.
"""

class RoleDAL:
    """
    Data Access Layer for user role management.
    """

    async def role_exists(self, role_id: str, db_session: AsyncSession) -> bool:
        """
        Check if a role exists by its unique ID.
        """
        result = await db_session.execute(select(Role).where(Role.role_id == role_id))
        print(f"Role exists: {role_id}",'--------------------------------')
        return result.scalar_one_or_none() is not None
    
    async def get_all_roles(self, db_session: AsyncSession) -> list[Role]:
        """
        List all user roles in the database.
        """
        result = await db_session.execute(select(Role))
        return result.scalars().all()
    
    async def create_role(self, role_data: RoleCreate, db_session: AsyncSession) -> Role:
        """
        Create a new user role, or return the existing one if it already exists by name.
        """
        # Check if the role already exists by name
        existing_role = await self.get_role_by_name(role_data.name,db_session)
        if existing_role:
            return existing_role  # Return the existing role if it already exists

        # Create a new role
        new_role = Role(
            name=role_data.name,
            description=role_data.description,
        )
        db_session.add(new_role)
        await db_session.commit()
        await db_session.refresh(new_role)

        return new_role


    async def get_role_by_id(self, role_id: str, db_session: AsyncSession) -> Role:
        """
        Retrieve a user role by its unique ID.
        """
        # Check if the role exists
        result = await db_session.execute(select(Role).where(Role.role_id == role_id))
        return result.scalar_one_or_none()

    async def get_role_by_name(self, name: str, db_session: AsyncSession) -> Role:
        """
        Retrieve a user role by its name.
        """
        result = await db_session.execute(
            select(Role).where(Role.name == name)
        )
        return result.scalar_one_or_none()

    async def update_role(self, role_id: str, role_data: RoleUpdate, db_session: AsyncSession) -> Role:
        """
        Update a user role by its ID.
        """
        role = await self.get_role_by_id(role_id,db_session)
        if not role:
            return None
        for key, value in role_data.model_dump(exclude_unset=True).items():
            setattr(role, key, value)
        await db_session.commit()
        await db_session.refresh(role)
        return role

    async def delete_role(self, role_id: str, db_session: AsyncSession) -> bool:
        """
        Delete a user role by its ID.
        """
        role = await self.get_role_by_id(role_id,db_session)
        if not role:
            return False
        await db_session.delete(role)
        await db_session.commit()
        return True