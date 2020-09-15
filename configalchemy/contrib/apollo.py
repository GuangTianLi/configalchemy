import json
import logging
import threading
import time
from http import HTTPStatus
from typing import Dict

import requests

from configalchemy import BaseConfig, ConfigType

time_counter = time.time


class ConfigException(Exception):
    ...


logger = logging.getLogger(__name__)


class ApolloBaseConfig(BaseConfig):
    CONFIGALCHEMY_ENABLE_FUNCTION = True

    APOLLO_USING_CACHE = False
    APOLLO_SERVER_URL = ""
    APOLLO_APP_ID = ""
    APOLLO_CLUSTER = "default"
    APOLLO_NAMESPACE = "application"

    APOLLO_EXTRA_NAMESPACE = ""
    APOLLO_EXTRA_NAMESPACE_PRIORITY = 9

    APOLLO_LONG_POLL_TIMEOUT = 80

    def __init__(self):
        self.apollo_notification_map: Dict[str, ConfigType] = {}
        super().__init__()

    def start_long_poll(self):
        logger.info("start long poll")
        thread = threading.Thread(target=self.long_poll)
        thread.daemon = True
        thread.start()
        return thread

    def _access_config_by_namespace(self, namespace: str) -> ConfigType:
        route = "configs"
        if self.APOLLO_USING_CACHE:
            route = "configfiles"
        url = (
            f"{self.APOLLO_SERVER_URL}/{route}/{self.APOLLO_APP_ID}/"
            f"{self.APOLLO_CLUSTER}/{namespace}"
        )
        logger.info(f"Access apollo server url: {url}")
        response = requests.get(url)
        if response.ok:
            data = response.json()
            self.apollo_notification_map.setdefault(data["namespaceName"], {"id": -1})
            self.apollo_notification_map[data["namespaceName"]]["data"] = data.get(
                "configurations", {}
            )
            logger.debug(f"Got from apollo: {data}")
            return data.get("configurations", {})
        else:
            raise ConfigException(f"loading config failed: {url}")

    def configuration_function(self) -> ConfigType:
        self.from_mapping(
            self._access_config_by_namespace(self.APOLLO_NAMESPACE),
            priority=self.CONFIGALCHEMY_FUNCTION_VALUE_PRIORITY,
        )
        for namespace in self.APOLLO_EXTRA_NAMESPACE.split(","):
            if namespace:
                self.from_mapping(
                    self._access_config_by_namespace(namespace),
                    priority=self.APOLLO_EXTRA_NAMESPACE_PRIORITY,
                )
        return {}

    def long_poll_from_apollo(self):
        url = f"{self.APOLLO_SERVER_URL}/notifications/v2/"
        notifications = []
        for key, value in self.apollo_notification_map.items():
            notifications.append({"namespaceName": key, "notificationId": value["id"]})

        r = requests.get(
            url=url,
            params={
                "appId": self.APOLLO_APP_ID,
                "cluster": self.APOLLO_CLUSTER,
                "notifications": json.dumps(notifications, ensure_ascii=False),
            },
            timeout=self.APOLLO_LONG_POLL_TIMEOUT,
        )

        if r.status_code == HTTPStatus.NOT_MODIFIED:
            logger.info("Apollo No change, loop...")
        elif r.status_code == HTTPStatus.OK:
            data = r.json()
            for entry in data:
                logger.info(
                    "%s has changes: notificationId=%d"
                    % (entry["namespaceName"], entry["notificationId"])
                )
                namespace = entry["namespaceName"]
                if namespace == self.APOLLO_NAMESPACE:
                    self.from_mapping(
                        self._access_config_by_namespace(namespace),
                        priority=self.CONFIGALCHEMY_FUNCTION_VALUE_PRIORITY,
                    )
                else:
                    self.from_mapping(
                        self._access_config_by_namespace(namespace),
                        priority=self.APOLLO_EXTRA_NAMESPACE_PRIORITY,
                    )
                self.apollo_notification_map[entry["namespaceName"]]["id"] = entry[
                    "notificationId"
                ]
        else:  # pragma: no cover
            raise ConfigException(f"{url} : unexpected status {r.status_code}")

    def long_poll(self):
        while True:
            try:
                logger.debug("start apollo configuration long poll")
                self.long_poll_from_apollo()
            except ConfigException:
                time.sleep(5)
