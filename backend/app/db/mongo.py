from app.config import Settings


async def create_mongo_indexes(settings: Settings) -> None:
    if not settings.mongodb_url:
        return
    from motor.motor_asyncio import AsyncIOMotorClient

    client = AsyncIOMotorClient(settings.mongodb_url)
    collection = client[settings.mongodb_database][settings.mongodb_collection]
    await collection.create_index("plate_number")
    await collection.create_index("created_at")
    await collection.create_index("status")
    client.close()
