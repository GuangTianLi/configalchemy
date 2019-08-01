import time
import unittest
from unittest.mock import Mock

import requests

from configalchemy.contrib.apollo import ApolloBaseConfig

return_value = {"namespaceName": "tmp", "configurations": {"TEST": "changed"}}


def mock_get(url: str, params: dict = None, timeout: int = 5):
    if "notifications" in url:
        return Mock(
            status_code=200,
            ok=False,
            json=Mock(
                return_value=[{"namespaceName": "application", "notificationId": 1}]
            ),
        )
    else:
        return Mock(status_code=200, ok=True, json=Mock(return_value=return_value))


class ApolloConfigTestCase(unittest.TestCase):
    def test_ApolloConfig(self):
        requests.get = mock_get
        long_poll = Mock()
        ApolloBaseConfig.start_long_poll = long_poll

        class DefaultConfig(ApolloBaseConfig):
            TEST = "base"
            ENABLE_LONG_POLL = True
            #: apollo
            APOLLO_SERVER_URL = ""
            APOLLO_APP_ID = ""
            APOLLO_CLUSTER = "default"
            APOLLO_NAMESPACE = "application"

        config = DefaultConfig()
        self.assertEqual("changed", config["TEST"])
        self.assertEqual(1, long_poll.call_count)

    def test_long_poll(self):
        class DefaultConfig(ApolloBaseConfig):
            TEST = "base"

            #: apollo
            APOLLO_SERVER_URL = ""
            APOLLO_APP_ID = ""
            APOLLO_CLUSTER = "default"
            APOLLO_NAMESPACE = "application"

        requests.get = mock_get
        return_value["namespaceName"] = "application"
        config = DefaultConfig()
        return_value["namespaceName"] = "tmp"
        self.assertEqual("changed", config.get_from_namespace("TEST", namespace="tmp"))
        thread = config.start_long_poll()
        time.sleep(1)
        self.assertEqual("changed", config["TEST"])


if __name__ == "__main__":
    unittest.main()
