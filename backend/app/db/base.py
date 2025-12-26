from app.logging_config import backend_logger as logger
from typing import Any, Generic, Sequence, Type, TypeVar
from pydantic import BaseModel
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import text
from app.db.utils import hash_data

async def check_db_connection(db: AsyncSession) -> bool:
    """
    Checks if a connection to the database can be established.
    Returns True if the connection is successful, False otherwise.
    """
    try:
        await db.execute(text("SELECT 1"))
        logger.info("Database connection successful.")
        return True
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return False

# --- Schema Management Functions ---
async def create_user_schema(db: AsyncSession, schema_name: str) -> bool:
    """
    Executes a raw SQL command to create a new schema if it doesn't already exist.
    This is an idempotent operation.
    """
    # Basic validation to prevent SQL injection with schema names
    if not schema_name.isidentifier():
        logger.error(f"Attempted to create a schema with an invalid name: {schema_name}")
        return False
        
    try:
        logger.info(f"Attempting to create schema '{schema_name}'...")
        await db.execute(text(f'CREATE SCHEMA IF NOT EXISTS "{schema_name}"'))
        logger.info(f"✅ Schema '{schema_name}' creation statement executed.")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to create schema '{schema_name}': {e}", exc_info=True)
        return False

# --- Generic CRUD Base Class ---

ModelType = TypeVar("ModelType")
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)

class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        self.model = model

    async def get(self, db: AsyncSession, id: Any) -> ModelType | None:
        """Get a single object by its ID."""
        statement = select(self.model).where(self.model.id == id)
        result = await db.execute(statement)
        return result.scalar_one_or_none()

    async def get_multi(
        self, db: AsyncSession, *, skip: int = 0, limit: int = 100
    ) -> Sequence[ModelType]:
        """Get multiple objects with pagination."""
        statement = select(self.model).offset(skip).limit(limit)
        result = await db.execute(statement)
        return result.scalars().all()

    async def create(self, db: AsyncSession, *, obj_in: CreateSchemaType | dict) -> ModelType:
        """
        Create a new object, automatically hashing any fields that have a
        corresponding `_hash` column in the model.
        """
        obj_in_data = obj_in if isinstance(obj_in, dict) else obj_in.model_dump()

        for field in list(obj_in_data.keys()):
            hash_field_name = f"{field}_hash"
            if hasattr(self.model, hash_field_name):
                value = obj_in_data[field]
                if isinstance(value, str):
                    obj_in_data[hash_field_name] = hash_data(value)

        db_obj = self.model(**obj_in_data)
        db.add(db_obj)
        await db.flush()
        await db.refresh(db_obj)
        return db_obj

    async def update(
        self, db: AsyncSession, *, db_obj: ModelType, obj_in: UpdateSchemaType | dict[str, Any]
    ) -> ModelType:
        """
        Update an existing object, automatically hashing any fields that have a
        corresponding `_hash` column in the model.
        """
        update_data = obj_in if isinstance(obj_in, dict) else obj_in.model_dump(exclude_unset=True)

        for field in list(update_data.keys()):
            hash_field_name = f"{field}_hash"
            if hasattr(self.model, hash_field_name):
                value = update_data[field]
                if isinstance(value, str):
                    update_data[hash_field_name] = hash_data(value)
        
        for field, value in update_data.items():
            setattr(db_obj, field, value)
            
        db.add(db_obj)
        await db.flush()
        await db.refresh(db_obj)
        return db_obj

    async def delete(self, db: AsyncSession, *, id: Any) -> ModelType | None:
        obj = await self.get(db, id=id)
        if obj:
            await db.delete(obj)
            await db.flush()
        return obj