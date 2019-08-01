import time
import unittest
from unittest.mock import Mock

import requests

from configalchemy.contrib.apollo import ApolloBaseConfig


class ApolloConfigTestCase(unittest.TestCase):
    def test_ApolloConfig(self):
        class DefaultConfig(ApolloBaseConfig):
            TEST = "base"
            #: apollo
            APOLLO_SERVER_URL = "http://apollo.service.gllue.net"
            APOLLO_APP_ID = "5b366db80139"
            APOLLO_CLUSTER = "default"
            APOLLO_NAMESPACE = "application"

        config = DefaultConfig()
        self.assertEqual("test", config["TEST"])

    def test_long_poll(self):
        class DefaultConfig(ApolloBaseConfig):
            TEST = "base"
            #: apollo
            APOLLO_SERVER_URL = "http://apollo.service.gllue.net"
            APOLLO_APP_ID = "5b366db80139"
            APOLLO_CLUSTER = "default"
            APOLLO_NAMESPACE = "application"

        config = DefaultConfig()
        return_value = {"namespaceName": "tmp", "configurations": {"TEST": "changed"}}

        def mock_get(url: str, params: dict = None, timeout: int = 5):
            if "notifications" in url:
                return Mock(
                    status_code=200,
                    ok=False,
                    json=Mock(
                        return_value=[
                            {"namespaceName": "application", "notificationId": 1}
                        ]
                    ),
                )
            else:
                return Mock(
                    status_code=200, ok=True, json=Mock(return_value=return_value)
                )

        requests.get = mock_get
        self.assertEqual("test", config["TEST"])
        self.assertEqual("changed", config.get_from_namespace("TEST", namespace="tmp"))
        thread = config.start_long_poll()
        time.sleep(1)
        self.assertEqual("changed", config["TEST"])


if __name__ == "__main__":
    unittest.main()
