
import unittest

# Imports
from pydantic import BaseModel, HttpUrl
from rest_api_client.lib import RestAPI, Endpoint, HTTPMethod
import httpx

class TestRestAPI(unittest.TestCase):
    def setUp(self):
        # Optionally declare your model classes
        class JokeModel(BaseModel):
            id: str
            created_at: str
            updated_at: str
            icon_url: str
            categories: list
            url: HttpUrl
            value: str

        self.joke_model = JokeModel
        # Declare your API endpoints

        self.endpoints = [

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
        self.client = httpx.Client()
        self.api = RestAPI(api_url="https://api.chucknorris.io/jokes", driver=self.client)
        self.api.register_endpoints(self.endpoints)
    
    def test_call_get_joke(self):
        joke = self.api.call_endpoint("get_joke")
        assert joke
        assert isinstance(joke, self.joke_model)

    def test_call_get_joke_sdk(self):
        joke = self.api.get_joke()
        assert joke
        assert isinstance(joke, self.joke_model)


    def test_get_categories_sdk(self):
        categories = self.api.get_categories()
        assert categories
        assert isinstance(categories, list)

    def test_get_search_sdk(self):
        search = self.api.get_search(query="something")
        assert search

    def tearDown(self):
        self.client.close()


if __name__ == '__main__':
    unittest.main()