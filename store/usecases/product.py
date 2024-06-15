from uuid import UUID
import pymongo
from motor.motor_asyncio import AsyncIOMotorClient
from store.db.mongo import db_client
from store.schemas.product import ProductIn, ProductOut, ProductUpdate, ProductUpdateOut
from store.core.exceptions import NotFoundException, BaseException
from store.models.product import ProductModel


class ProductUsecase:
    def __init__(self) -> None:
        self.client: AsyncIOMotorClient = db_client.get()
        self.database = self.client.get_database()
        self.collection = self.database.get_collection("products")

    async def create(self, body: ProductIn) -> ProductOut:
        product_model = ProductModel(**body.model_dump())
        if product_model.price < 0 or product_model.quantity < 0:
            raise BaseException("Incorrect value sent")
        await self.collection.insert_one(product_model.model_dump())
        return ProductOut(**product_model.model_dump())

    async def get(self, id: UUID) -> ProductOut:
        product = await self.collection.find_one({"id": id})
        if not product:
            raise NotFoundException(
                message=f"Product not found with filter: UUID('{id}')"
            )
        return ProductOut(**product)

    async def query(self) -> list[ProductOut]:
        return [ProductOut(**item) async for item in self.collection.find()]

    async def query_specific(self, filter: dict) -> list[ProductOut]:
        return [ProductOut(**item) async for item in self.collection.find(filter)]

    async def update(self, id: UUID, body: ProductUpdate) -> ProductUpdateOut:
        product = await self.collection.find_one({"id": id})
        if not product:
            raise BaseException(f"UUID Not Found: {id}")
        result = await self.collection.find_one_and_update(
            filter={"id": id},
            update={"$set": body.model_dump(exclude_none=True)},
            return_document=pymongo.ReturnDocument.AFTER,
        )
        return ProductUpdateOut(**result)

    async def delete(self, id: UUID):
        product = await self.collection.find_one({"id": id})
        if not product:
            raise NotFoundException(
                message=f"Product not found with filter: UUID('{id}')"
            )

        result = await self.collection.delete_one({"id": id})
        return True if result.deleted_count > 0 else False


product_usecase = ProductUsecase()
