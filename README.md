# Python Rest API Client

![pypi](https://img.shields.io/pypi/v/py-rest-api-client)
![coverage](https://github.com/paolorechia/rest-api-client/blob/master/coverage.svg?raw=true)

-----

Glues pydantic and httpx to provide a simple REST API client, with dynamic generated methods.
It supports both synchronous and asynchronous formats.

Roadmap:
- Adds Authentication support
- Auto generate models from OpenAPI (3) Spec
- Export generated source code

---


### Usage

```python

CHUCK_BASE_URL = "https://api.chucknorris.io/jokes"

# Imports
from pydantic import BaseModel, HttpUrl
from rest_api_client.lib import RestAPI, Endpoint, HTTPMethod
import httpx

# Optionally declare your model classes
class JokeModel(BaseModel):
    id: str
    created_at: str
    updated_at: str
    icon_url: str
    categories: list
    url: str
    value: str


# Declare your API endpoints

endpoints = [

    # Fully descriptive declaration.
    Endpoint(
        name="get_joke",
        path="/random",
        method=HTTPMethod.GET,
        model=JokeModel,
        query_parameters=[("category", str)],
    ),

    # No model provided, result comes back as a dictionary.
    Endpoint(
        name="get_categories",
        path="/categories",
        method=HTTPMethod.GET,
    ),
    
    # Omit HTTP Method, it gets inferred from the endpoint name.
    Endpoint(name="get_search", path="/search", query_parameters=[("query", str)]),
]

# Instantiate your HTTP client session. Should also work with requests

with httpx.Client() as client:
    api = RestAPI(api_url=CHUCK_BASE_URL, driver=client)
    api.register_endpoints(endpoints)

    joke = api.call_endpoint("get_joke")
    joke2 = api.get_joke()

    categories = api.get_categories()

    search = api.get_search(query="something")

    print(joke)
    print(joke2)
    print(search)
```

Another example for pastry (see integration tests).
```python

api = RestAPI(
    api_url="https://getpantry.cloud/apiv1",
    driver=client,
    # One can also pass endpoints to the constructor
    endpoints=[
        Endpoint(name="get_pantry", path="/pantry/{pantry_id}"),
        Endpoint(
            name="get_basket",
            # Path parameters can be provided in the format {variable_name}
            path="/pantry/{pantry_id}/basket/{basket_id}",
        ),
        Endpoint(
            # 'create_' is interpreted as POST
            name="create_basket",
            path="/pantry/{pantry_id}/basket/{basket_id}",
        ),
        Endpoint(
            # 'update_' is interpreted as PUT
            name="update_basket",
            path="/pantry/{pantry_id}/basket/{basket_id}",
        ),
        Endpoint(
            name="delete_basket",
            path="/pantry/{pantry_id}/basket/{basket_id}",
        ),
    ],
)
pantries = api.get_pantry(pantry_id="123")

# Create/update/patch methods have an additional parameter called data
# Which is passed as the BODY of the request
api.create_basket(pantry_id="123", basket_id="234", data={"key": "value"})
api.update_basket(pantry_id="123", basket_id="234", data={"key2": "value2"})

basket = api.get_basket(pantry_id="123", basket_id="234")
api.delete_basket(pantry_id="123", basket_id="234")
```

If pantry supported PATCH, we would declare the endpoint as:

```python
Endpoint(
    name="patch_basket",  # No alias for patch exists
    path="/pantry/{pantry_id}/basket/{basket_id}",
),
```


#### Async methods
By default, async methods are created with the prefix `_async`.
For instance:

```python3
await api.async_get_pantry(pantry_id="123")
await api.async_create_basket(
    pantry_id="123", basket_id="234", data={"key": "value"}
)
await api.async_update_basket(
    pantry_id="123", basket_id="234", data={"key2": "value2"}
)
await api.async_get_basket(pantry_id="123", basket_id="234")
await api.async_delete_basket(pantry_id="123", basket_id="234")
```
