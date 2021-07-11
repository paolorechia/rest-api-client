from unittest.mock import MagicMock
from pydantic import BaseModel, HttpUrl
from rest_api_client.lib import RestAPI, Endpoint, HTTPMethod
import httpx

CHUCK_BASE_URL = "https://api.chucknorris.io/jokes"

example_response = {
    "categories": [],
    "created_at": "2020-01-05 13:42:24.40636",
    "icon_url": "https://assets.chucknorris.host/img/avatar/chuck-norris.png",
    "id": "fMxB6_A2Qku_tKeo5jzRiA",
    "updated_at": "2020-01-05 13:42:24.40636",
    "url": "https://api.chucknorris.io/jokes/fMxB6_A2Qku_tKeo5jzRiA",
    "value": "America's next top model is really a competition of who gets to have Chuck Norris's child.",  # noqa: E501
}

categories = [
    "animal",
    "career",
    "celebrity",
    "dev",
    "explicit",
    "fashion",
    "food",
    "history",
    "money",
    "movie",
    "music",
    "political",
    "religion",
    "science",
    "sport",
    "travel",
]

animal_category = {
    "categories": ["animal"],
    "created_at": "2020-01-05 13:42:19.576875",
    "icon_url": "https://assets.chucknorris.host/img/avatar/chuck-norris.png",
    "id": "bmom6jqftpqgokh8adtolw",
    "updated_at": "2020-01-05 13:42:19.576875",
    "url": "https://api.chucknorris.io/jokes/bmom6jqftpqgokh8adtolw",
    "value": "Chuck Norris once rode a nine foot grizzly bear through an automatic car wash, instead of taking a shower.",
}


class JokeModel(BaseModel):
    id: str
    created_at: str
    updated_at: str
    icon_url: str
    categories: list
    url: HttpUrl
    value: str


def test_rest_api():

    endpoints = [
        Endpoint(
            name="get_joke",
            path="/random",
            method=HTTPMethod.GET,
            model=JokeModel,
            query_parameters=[("category", str)],
        ),
        Endpoint(
            name="get_categories",
            path="/categories",
            method=HTTPMethod.GET,
        ),
        Endpoint(name="get_search", path="/search", query_parameters=[("query", str)]),
    ]
    client = MagicMock(spec=httpx.Client)
    client.get().json.side_effect = [
        example_response,
        example_response,
        example_response,
        categories,
        example_response,
    ]
    api = RestAPI(api_url=CHUCK_BASE_URL, driver=client)
    api.register_endpoints(endpoints)

    joke = api.call_endpoint("get_joke")
    assert isinstance(joke, JokeModel)
    for key, item in example_response.items():
        assert item == getattr(joke, key)

    joke2 = api.get_joke()
    assert joke == joke2

    api.get_joke(category="doesitwork?")

    assert api.get_categories() == categories

    api.get_search(query="something")
