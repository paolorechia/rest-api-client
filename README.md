# Python Rest API Client (WIP)
Work in progress. Aims at glueing pydantic and httpx with a simple REST API client, with dynamic generated methods.
Ideally, it could be support both synchronous and asynchronous formats.

Currently it is only supporting GET, POST, PUT Methods, since it's a work in progress.
Roadmap:

- PATCH, DELETE
- Adds Authentication support
- Adds Async invokation support
- Export generated source code
- Auto generate models from OpenAPI (3) Spec

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

    categories = api.get_categoires()

    search = api.get_search(query="something")

    print(joke)
    print(joke2)
    print(search)
```

Another example for pastry (see integration tests).
```
        self.api = RestAPI(
            api_url="https://getpantry.cloud/apiv1",
            driver=self.client,
            endpoints=[
                Endpoint(
                    name="create_basket",
                    path="/pantry/{pantry_id}/basket/{basket_id}",
                    method=HTTPMethod.POST,
                )
            ],
        )

    def test_pantry(self):
        self.api.create_basket(pantry_id=self.pantry_id, basket_id="test_bucket", data={
            "Test": "Hello world!"
        })
```
