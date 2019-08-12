import json
import logging
import threading
import time

import requests

from ..configalchemy import BaseConfig, ConfigType

time_counter = time.time


class ConfigException(Exception):
    ...


class ApolloBaseConfig(BaseConfig):
    CONFIGALCHEMY_ENABLE_FUNCTION = True

    #: apollo
    APOLLO_USING_CACHE = False
    APOLLO_SERVER_URL = ""
    APOLLO_APP_ID = ""
    APOLLO_CLUSTER = "default"
    APOLLO_NAMESPACE = "application"
    APOLLO_LONG_POLL_TIMEOUT = 80
    ENABLE_LONG_POLL = False
    APOLLO_NOTIFICATION_MAP: ConfigType = {}

    def __init__(self):
        super().__init__()
        if self.get("ENABLE_LONG_POLL", False):
            self.start_long_poll()

    def get_from_namespace(
        self, key: str, namespace: str = "application", default=None
    ):
        if namespace not in self.APOLLO_NOTIFICATION_MAP:
            self.APOLLO_NAMESPACE = namespace
            self.sync_function()
        return self.APOLLO_NOTIFICATION_MAP[namespace]["data"].get(key, default)

    def start_long_poll(self):
        logging.info("start long poll")
        thread = threading.Thread(target=self.long_poll)
        thread.daemon = True
        thread.start()
        return thread

    def sync_function(self) -> ConfigType:
        route = "configs"
        if self.APOLLO_USING_CACHE:
            route = "configfiles"
        url = (
            f"{self.APOLLO_SERVER_URL}/{route}/{self.APOLLO_APP_ID}/"
            f"{self.APOLLO_CLUSTER}/{self.APOLLO_NAMESPACE}"
        )
        response = requests.get(url)
        if response.ok:
            data = response.json()
            self.APOLLO_NOTIFICATION_MAP.setdefault(data["namespaceName"], {"id": -1})
            self.APOLLO_NOTIFICATION_MAP[data["namespaceName"]]["data"] = data.get(
                "configurations", {}
            )
            logging.debug(f"Got from apollo: {data}")
            return data.get("configurations", {})
        else:
            raise ConfigException("loading config failed")

    def long_poll_from_apollo(self):
        url = f"{self.APOLLO_SERVER_URL}/notifications/v2/"
        notifications = []
        for key, value in self.APOLLO_NOTIFICATION_MAP.items():
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

        if r.status_code == 304:
            logging.info("Apollo No change, loop...")
        elif r.status_code == 200:
            data = r.json()
            for entry in data:
                logging.info(
                    "%s has changes: notificationId=%d"
                    % (entry["namespaceName"], entry["notificationId"])
                )
                self.APOLLO_NAMESPACE = entry["namespaceName"]
                self.access_config_from_function(
                    priority=self.CONFIGALCHEMY_FUNCTION_VALUE_PRIORITY
                )
                self.APOLLO_NOTIFICATION_MAP[entry["namespaceName"]]["id"] = entry[
                    "notificationId"
                ]
        else:
            logging.info("Sleep...")

    def long_poll(self):
        start_time = time_counter()

        while True:
            try:
                logging.debug("start long poll")
                self.long_poll_from_apollo()
                now = time_counter()
                if now - start_time > 300:
                    for namespace in self.APOLLO_NOTIFICATION_MAP:
                        self.APOLLO_NAMESPACE = namespace
                        self.access_config_from_function(
                            priority=self.CONFIGALCHEMY_FUNCTION_VALUE_PRIORITY
                        )
                    start_time = time_counter()
            except ConfigException:
                time.sleep(5)
            except Exception:
                logging.exception("long poll error")
