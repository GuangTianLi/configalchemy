import time
import unittest
from unittest.mock import Mock, patch

import requests

import configalchemy.contrib.apollo
from configalchemy.contrib.apollo import ApolloBaseConfig, ConfigException

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
    @patch.object(ApolloBaseConfig, "start_long_poll")
    def test_ApolloConfig(self, start_long_poll):
        requests.get = mock_get

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
        self.assertEqual(1, start_long_poll.call_count)

    @patch.object(requests, "get")
    @patch.object(configalchemy.contrib.apollo, "time_counter")
    @patch.object(time, "sleep")
    def test_long_poll(self, time_sleep, time_counter, requests_get):
        class DefaultConfig(ApolloBaseConfig):
            TEST = "base"
            CONFIGALCHEMY_ENABLE_FUNCTION = False
            #: apollo
            APOLLO_SERVER_URL = ""
            APOLLO_APP_ID = ""
            APOLLO_CLUSTER = "default"
            APOLLO_NAMESPACE = "application"

        count = 0

        def time_counter_side_effect():
            nonlocal count
            if count == 0:
                count += 1
                return 0
            elif count == 1:
                count += 1
                return 99999
            else:
                raise ConfigException("break")

        config = DefaultConfig()
        requests_get.side_effect = mock_get

        self.assertEqual("changed", config.get_from_namespace("TEST", namespace="tmp"))
        return_value["namespaceName"] = "application"
        time_counter.side_effect = time_counter_side_effect
        time_sleep.side_effect = ConfigException("break")

        with self.assertRaises(ConfigException):
            config.long_poll()

        self.assertEqual("changed", config["TEST"])
        self.assertIn("application", config.APOLLO_NOTIFICATION_MAP)

    def test_start_long_poll(self):
        class DefaultConfig(ApolloBaseConfig):
            CONFIGALCHEMY_ENABLE_FUNCTION = False

        config = DefaultConfig()
        with patch("threading.Thread") as MockThread:
            config.start_long_poll()
            MockThread.assert_called_with(target=config.long_poll)


if __name__ == "__main__":
    unittest.main()
