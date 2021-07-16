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

    def tearDown(self):
        self.client.close()


if __name__ == "__main__":
    unittest.main()
