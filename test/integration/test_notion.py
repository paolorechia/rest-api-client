from rest_api_client.lib import RestAPI, Endpoint, HTTPMethod
from rest_api_client.lib import BearerHeaderToken
import httpx
import unittest
import re
import logging


def api_setup(self):
    with open("/Users/paolo/.notion-token", "r") as fp:
        self.notion_token = fp.read()
        self.notion_token = re.sub("\n", "", self.notion_token)
        print(self.notion_token)

    self.auth = BearerHeaderToken(bearer_token=self.notion_token)
    self.api = RestAPI(
        api_url="https://api.notion.com/v1",
        driver=None,
        endpoints=[
            Endpoint(name="search", path="/search", method=HTTPMethod.POST),
        ],
        custom_headers={"Notion-Version": "2021-05-13"},
    )


class TestNotion(unittest.TestCase):
    def setUp(self):
        api_setup(self)
        self.client = httpx.Client(auth=self.auth)
        self.api.driver = self.client
        logger = logging.getLogger("LIB_LOGGER")
        logger.setLevel(logging.DEBUG)

    def test_search(self):
        self.api.search(data={"query": "Test page"})

    def tearDown(self):
        self.client.close()


if __name__ == "__main__":
    unittest.main()
