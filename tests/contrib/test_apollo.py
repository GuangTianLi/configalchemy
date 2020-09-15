import threading
import time
import unittest
from unittest.mock import Mock, patch

import requests

from configalchemy.contrib.apollo import ApolloBaseConfig, ConfigException, logger


class ApolloConfigTestCase(unittest.TestCase):
    @patch.object(requests, "get")
    @patch.object(ApolloBaseConfig, "start_long_poll")
    def test_ApolloConfig(self, start_long_poll, requests_get):
        return_value = {
            "namespaceName": "application",
            "configurations": {"TEST": "test"},
        }

        requests_get.side_effect = lambda *a, **kw: Mock(
            status_code=200, ok=True, json=Mock(return_value=return_value)
        )

        class DefaultConfig(ApolloBaseConfig):
            TEST = "base"
            #: apollo
            APOLLO_SERVER_URL = ""
            APOLLO_APP_ID = ""
            APOLLO_CLUSTER = "default"
            APOLLO_NAMESPACE = "application"

        config = DefaultConfig()
        config.start_long_poll()
        self.assertEqual("test", config["TEST"])
        self.assertEqual(1, start_long_poll.call_count)

    @patch.object(requests, "get")
    @patch.object(logger, "debug")
    @patch.object(time, "sleep")
    def test_long_poll(self, time_sleep, logging_debug, requests_get):
        class DefaultConfig(ApolloBaseConfig):
            TEST = "base"
            CONFIGALCHEMY_ENABLE_FUNCTION = True
            #: apollo
            APOLLO_SERVER_URL = ""
            APOLLO_APP_ID = ""
            APOLLO_CLUSTER = "default"
            APOLLO_NAMESPACE = "application"
            APOLLO_EXTRA_NAMESPACE = "test"

        application_return_value = {
            "namespaceName": "application",
            "configurations": {"TEST": "application"},
        }

        def mock_get(url: str, **kwargs):
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
            elif "test" in url:
                return Mock(
                    status_code=200,
                    ok=True,
                    json=Mock(
                        return_value={
                            "namespaceName": "test",
                            "configurations": {"TEST": "test"},
                        }
                    ),
                )
            else:
                return Mock(
                    status_code=200,
                    ok=True,
                    json=Mock(return_value=application_return_value),
                )

        requests_get.side_effect = mock_get
        config = DefaultConfig()
        self.assertEqual("application", config.TEST)
        application_return_value["configurations"] = {"TEST": "changed"}

        count = 0

        def logging_debug_call(*args, **kwargs):
            nonlocal count
            if count == 0:
                count += 1
                return 0
            elif count == 1:
                count += 1
                return 99999
            else:
                raise ConfigException("break")

        logging_debug.side_effect = logging_debug_call
        time_sleep.side_effect = ConfigException("break")

        with self.assertRaises(ConfigException):
            config.long_poll()

        self.assertEqual("changed", config.TEST)
        self.assertIn("application", config.apollo_notification_map)
        self.assertIn("test", config.apollo_notification_map)

    @patch.object(threading, "Thread")
    def test_start_long_poll(self, thread_mock):
        class DefaultConfig(ApolloBaseConfig):
            CONFIGALCHEMY_ENABLE_FUNCTION = False

        config = DefaultConfig()
        config.start_long_poll()
        thread_mock.assert_called_with(target=config.long_poll)


if __name__ == "__main__":
    unittest.main()
