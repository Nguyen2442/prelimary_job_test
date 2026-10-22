import math
import os
import random
import threading
from datetime import datetime, timezone
from typing import Dict, List, Optional
from faker import Faker
from fastapi import FastAPI, Query
from pydantic import BaseModel

fake = Faker()
app = FastAPI(title="Emulating Vietful Inventory Service")


class ProductDto(BaseModel):
    productId: int
    sku: str
    partnerSKU: str
    productName: str
    color: Optional[str] = None
    size: Optional[str] = None
    description: Optional[str] = None
    isActive: bool = True


class InvProductBriefDto(BaseModel):
    warehouseCode: str
    partnerSKU: str
    sku: str
    physicalQty: int
    availableQty: int
    pendingInQty: int
    pendingOutQty: int
    freezeQty: int
    lastUpdatedDate: datetime


class InventoryPage(BaseModel):
    pageIndex: int
    pageSize: int
    totalCount: int
    totalPages: int
    indexFrom: int = 0
    items: List[InvProductBriefDto]
    hasPreviousPage: bool
    hasNextPage: bool


class CreateProductDto(BaseModel):
    sku: str
    partnerSKU: Optional[str] = None
    productName: str
    color: Optional[str] = None
    size: Optional[str] = None
    description: Optional[str] = None


class CreateProductResponseDto(BaseModel):
    productId: int
    sku: str
    partnerSKU: str
    status: bool
    errors: List[Dict[str, str]] = []


products: List[ProductDto] = []
inventories: Dict[str, InvProductBriefDto] = {}

lock = threading.Lock()


def now() -> datetime:
    return datetime.now(timezone.utc)


def add_product(dto: CreateProductDto, qty: int) -> ProductDto:
    product = ProductDto(
        productId=1001 + len(products),
        partnerSKU=dto.partnerSKU or dto.sku,
        **dto.model_dump(exclude={"partnerSKU"}),
    )
    products.append(product)
    inventories[product.sku] = InvProductBriefDto(
        warehouseCode=random.choice(["WH-HCM-01", "WH-HN-01"]),
        partnerSKU=product.partnerSKU,
        sku=product.sku,
        physicalQty=qty,
        availableQty=qty,
        pendingInQty=0,
        pendingOutQty=0,
        freezeQty=0,
        lastUpdatedDate=now(),
    )
    return product


def fake_product() -> CreateProductDto:
    n = 1001 + len(products)
    return CreateProductDto(
        sku=f"VF-{n}",
        partnerSKU=f"P-{n}",
        productName=fake.catch_phrase(),
        color=fake.color_name(),
        size=random.choice(["S", "M", "L"]),
        description=fake.sentence(nb_words=8),
    )


def page(items: list, page_index: int, page_size: int) -> list:
    start = page_index * page_size
    return items[start : start + page_size]


for _ in range(int(os.getenv("VIETFUL_INITIAL_PRODUCTS", "50"))):
    add_product(fake_product(), qty=random.randint(20, 500))


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/api/v1/Products", response_model=List[ProductDto])
def get_products(
    PageIndex: int = Query(default=0, ge=0),
    PageSize: int = Query(default=10, ge=1, le=200),
):
    with lock:
        return page(products, PageIndex, PageSize)


@app.post("/api/v1/Products", response_model=List[CreateProductResponseDto])
def create_products(body: List[CreateProductDto]):
    results = []
    with lock:
        for dto in body:
            if dto.sku in inventories:
                results.append(
                    CreateProductResponseDto(
                        productId=0,
                        sku=dto.sku,
                        partnerSKU=dto.partnerSKU or dto.sku,
                        status=False,
                        errors=[{"code": "DUPLICATE_SKU", "message": "SKU already exists"}],
                    )
                )
                continue
            p = add_product(dto, qty=0)
            results.append(CreateProductResponseDto(productId=p.productId, sku=p.sku, partnerSKU=p.partnerSKU, status=True))
    return results


@app.get("/api/v1/Products/inventories", response_model=InventoryPage)
def get_inventories(
    PageIndex: int = Query(default=0, ge=0),
    PageSize: int = Query(default=10, ge=1, le=200),
):
    with lock:
        all_items = list(inventories.values())
    total = len(all_items)
    total_pages = math.ceil(total / PageSize)
    return InventoryPage(
        pageIndex=PageIndex,
        pageSize=PageSize,
        totalCount=total,
        totalPages=total_pages,
        items=page(all_items, PageIndex, PageSize),
        hasPreviousPage=PageIndex > 0,
        hasNextPage=PageIndex + 1 < total_pages,
    )


@app.post("/admin/mutate", response_model=List[InvProductBriefDto])
def mutate(new_products: int = 2, update_products: int = 3):
    changed = []
    with lock:
        for inv in random.sample(list(inventories.values()), k=min(update_products, len(inventories))):
            delta = random.randint(1, 40)
            inv.physicalQty += delta
            inv.availableQty += delta
            inv.lastUpdatedDate = now()
            changed.append(inv)
        for _ in range(new_products):
            p = add_product(fake_product(), qty=random.randint(20, 500))
            changed.append(inventories[p.sku])
    return changed
