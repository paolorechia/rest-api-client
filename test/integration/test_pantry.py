from rest_api_client.lib import RestAPI, Endpoint, HTTPMethod
import httpx
import unittest
import re


def pantry_setup(self):
    with open("/Users/paolo/.pyrest-pantry-id", "r") as fp:
        self.pantry_id = fp.read()
        self.pantry_id = re.sub("\n", "", self.pantry_id)
        print(self.pantry_id)

    self.api = RestAPI(
        api_url="https://getpantry.cloud/apiv1",
        driver=None,
        endpoints=[
            Endpoint(name="get_pantry", path="/pantry/{pantry_id}"),
            Endpoint(
                name="get_basket",
                path="/pantry/{pantry_id}/basket/{basket_id}",
            ),
            Endpoint(
                name="create_basket",
                path="/pantry/{pantry_id}/basket/{basket_id}",
                method=HTTPMethod.POST,
            ),
            Endpoint(
                name="update_basket",
                path="/pantry/{pantry_id}/basket/{basket_id}",
                method=HTTPMethod.PUT,
            ),
            Endpoint(
                name="delete_basket", path="/pantry/{pantry_id}/basket/{basket_id}"
            ),
        ],
    )


class TestPantry(unittest.TestCase):
    def setUp(self):
        pantry_setup(self)
        self.client = httpx.Client()
        self.api.driver = self.client

    def test_create_bucket(self):
        self.api.create_basket(
            pantry_id=self.pantry_id,
            basket_id="test_bucket",
            data={"Test": "Hello world!"},
        )

    def test_get_bucket(self):
        get_bucket = {"Get": "Hello world!"}
        self.api.create_basket(
            pantry_id=self.pantry_id, basket_id="get_bucket", data=get_bucket
        )
        b2 = self.api.get_basket(pantry_id=self.pantry_id, basket_id="get_bucket")
        assert get_bucket == b2

    def test_update_bucket(self):
        update_bucket = {"Create": "Hello world!"}
        self.api.create_basket(
            pantry_id=self.pantry_id, basket_id="update_bucket", data=update_bucket
        )
        update_bucket["Updated"] = "New Key"
        self.api.update_basket(
            pantry_id=self.pantry_id, basket_id="update_bucket", data=update_bucket
        )
        b2 = self.api.get_basket(pantry_id=self.pantry_id, basket_id="update_bucket")
        assert b2 == update_bucket

    def test_delete_bucket(self):
        self.api.create_basket(
            pantry_id=self.pantry_id,
            basket_id="delete_bucket",
            data={"Test Delete": "OK!"},
        )
        self.api.delete_basket(pantry_id=self.pantry_id, basket_id="delete_bucket")

    def tearDown(self):
        self.client.close()


class TestAsyncPantry(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        pantry_setup(self)
        self.client = httpx.AsyncClient()
        self.api.driver = self.client

    async def test_create_bucket(self):
        await self.api.async_create_basket(
            pantry_id=self.pantry_id,
            basket_id="test_bucket",
            data={"Test": "Hello world!"},
        )

    async def test_get_bucket(self):
        get_bucket = {"Get": "Hello world!"}
        await self.api.async_create_basket(
            pantry_id=self.pantry_id, basket_id="get_bucket", data=get_bucket
        )
        b2 = await self.api.async_get_basket(
            pantry_id=self.pantry_id, basket_id="get_bucket"
        )
        assert get_bucket == b2

    async def test_update_bucket(self):
        update_bucket = {"Create": "Hello world!"}
        await self.api.async_create_basket(
            pantry_id=self.pantry_id, basket_id="update_bucket", data=update_bucket
        )
        update_bucket["Updated"] = "New Key"
        await self.api.async_update_basket(
            pantry_id=self.pantry_id, basket_id="update_bucket", data=update_bucket
        )
        b2 = await self.api.async_get_basket(
            pantry_id=self.pantry_id, basket_id="update_bucket"
        )
        assert b2 == update_bucket

    async def test_delete_bucket(self):
        await self.api.async_create_basket(
            pantry_id=self.pantry_id,
            basket_id="delete_bucket",
            data={"Test Delete": "OK!"},
        )
        await self.api.async_delete_basket(
            pantry_id=self.pantry_id, basket_id="delete_bucket"
        )

    async def asyncTearDown(self):
        await self.client.aclose()


if __name__ == "__main__":
    unittest.main()
