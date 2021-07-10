from typing import Iterable
from pydantic import BaseModel
from enum import Enum


class HTTPMethod(Enum):
    GET = "get"
    DELETE = "delete"
    POST = "post"
    PUT = "put"
    PATCH = "patch"


class Endpoint(BaseModel):
    path: str
    method: HTTPMethod
    model: BaseModel


class RestAPI:
    def register_endpoints(self, endpoints: Iterable[Endpoint]):
        pass
