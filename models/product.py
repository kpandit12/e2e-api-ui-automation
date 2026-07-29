"""Product/basket-related Pydantic models."""

from pydantic import BaseModel


class Product(BaseModel):
    """A Juice Shop product, as returned by ``GET /rest/products/search``."""

    id: int
    name: str
    description: str | None = None
    price: float
    image: str | None = None


class BasketItem(BaseModel):
    """A single line item in a basket."""

    id: int | None = None
    ProductId: int
    BasketId: int | str
    quantity: int = 1
