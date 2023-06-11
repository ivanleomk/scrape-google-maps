from enum import Enum
from typing import Optional

from pydantic import BaseModel


class Status(Enum):
    CLOSED = "Closed"
    TEMPORARILY_CLOSED = "Temporarily Closed"
    OPEN = "Open"


class Listing(BaseModel):
    title: str
    rating: Optional[float]
    number_of_reviews: Optional[int]
    address: Optional[str]
    review: str
    hasDelivery: bool
    hasTakeaway: bool
    hasDineIn: bool
    category: Optional[str]
    status: str
    url: str
    address: str
    long: float
    lat: float
