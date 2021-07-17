from rest_api_client.lib import RestAPI, Endpoint, HTTPMethod
import httpx
import unittest
import re


class TestPantry(unittest.TestCase):
    def setUp(self):
        with open("/Users/paolo/.pyrest-pantry-id", "r") as fp:
            self.pantry_id = fp.read()
            self.pantry_id = re.sub("\n", "", self.pantry_id)
            print(self.pantry_id)

        self.client = httpx.Client()

        self.api = RestAPI(
            api_url="https://getpantry.cloud/apiv1",
            driver=self.client,
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
        b2 = self.api.get_basket(
            pantry_id=self.pantry_id, basket_id="update_bucket"
        )
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


if __name__ == "__main__":
    unittest.main()
