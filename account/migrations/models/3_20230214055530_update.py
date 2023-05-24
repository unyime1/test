from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "pixabayimage" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "deleted" BOOL NOT NULL  DEFAULT False,
    "image_id" INT,
    "tags" TEXT,
    "page_url" VARCHAR(1000),
    "preview_url" VARCHAR(1000),
    "large_url" VARCHAR(1000),
    "full_hd_url" VARCHAR(1000)
);
COMMENT ON TABLE "pixabayimage" IS 'Image asset from Pixabay source';;
        CREATE TABLE IF NOT EXISTS "pixabayvideo" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "deleted" BOOL NOT NULL  DEFAULT False,
    "video_id" INT,
    "duration_sec" INT,
    "tags" TEXT,
    "page_url" VARCHAR(1000),
    "large_url" VARCHAR(1000),
    "medium_url" VARCHAR(1000)
);
COMMENT ON TABLE "pixabayvideo" IS 'Video asset from Pixabay.';;
        DROP TABLE IF EXISTS "media";"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS "pixabayimage";
        DROP TABLE IF EXISTS "pixabayvideo";"""
