from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "media" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "deleted" BOOL NOT NULL  DEFAULT False,
    "filename" VARCHAR(3000),
    "file_type" VARCHAR(3000),
    "filesize" DOUBLE PRECISION,
    "source_service" VARCHAR(500),
    "credits" VARCHAR(500),
    "source_link" VARCHAR(500),
    "remote_link" VARCHAR(500)
);;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS "media";"""
