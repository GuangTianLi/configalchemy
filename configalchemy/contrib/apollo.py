import json
import logging
import threading
import time
from typing import Any, Callable, Coroutine, List

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

    def __init__(
        self,
        function_list: List[Callable[[Any], ConfigType]] = None,
        coroutine_function_list: List[
            Callable[[Any], Coroutine[Any, Any, ConfigType]]
        ] = None,
        root_path: str = "",
    ):
        function_list = function_list or []
        function_list.append(access_config_from_apollo)
        super().__init__(function_list, coroutine_function_list)
        if self.get("ENABLE_LONG_POLL", False):
            self.start_long_poll()

    def get_from_namespace(
        self, key: str, namespace: str = "application", default=None
    ):
        if namespace not in self.APOLLO_NOTIFICATION_MAP:
            self.APOLLO_NAMESPACE = namespace
            access_config_from_apollo(self)
        return self.APOLLO_NOTIFICATION_MAP[namespace]["data"].get(key, default)

    def start_long_poll(self):
        logging.info("start long poll")
        thread = threading.Thread(target=long_poll, kwargs={"current_config": self})
        thread.daemon = True
        thread.start()
        return thread


def access_config_from_apollo(current_config: ApolloBaseConfig) -> dict:
    route = "configs"
    if current_config.APOLLO_USING_CACHE:
        route = "configfiles"
    url = (
        f"{current_config.APOLLO_SERVER_URL}/{route}/{current_config.APOLLO_APP_ID}/"
        f"{current_config.APOLLO_CLUSTER}/{current_config.APOLLO_NAMESPACE}"
    )
    response = requests.get(url)
    if response.ok:
        data = response.json()
        current_config.APOLLO_NOTIFICATION_MAP.setdefault(
            data["namespaceName"], {"id": -1}
        )
        current_config.APOLLO_NOTIFICATION_MAP[data["namespaceName"]][
            "data"
        ] = data.get("configurations", {})
        logging.debug(f"Got from apollo: {data}")
        return data.get("configurations", {})
    else:
        raise ConfigException("loading config failed")


def long_poll_from_apollo(current_config: ApolloBaseConfig):
    url = f"{current_config.APOLLO_SERVER_URL}/notifications/v2/"
    notifications = []
    for key, value in current_config.APOLLO_NOTIFICATION_MAP.items():
        notifications.append({"namespaceName": key, "notificationId": value["id"]})

    r = requests.get(
        url=url,
        params={
            "appId": current_config.APOLLO_APP_ID,
            "cluster": current_config.APOLLO_CLUSTER,
            "notifications": json.dumps(notifications, ensure_ascii=False),
        },
        timeout=current_config.APOLLO_LONG_POLL_TIMEOUT,
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
            current_config.APOLLO_NAMESPACE = entry["namespaceName"]
            current_config.access_config_from_function_list(
                priority=current_config.CONFIGALCHEMY_FUNCTION_VALUE_PRIORITY
            )
            current_config.APOLLO_NOTIFICATION_MAP[entry["namespaceName"]][
                "id"
            ] = entry["notificationId"]
    else:
        logging.info("Sleep...")


def long_poll(current_config: ApolloBaseConfig):
    start_time = time_counter()

    while True:
        try:
            logging.debug("start long poll")
            long_poll_from_apollo(current_config)
            now = time_counter()
            if now - start_time > 300:
                for namespace in current_config.APOLLO_NOTIFICATION_MAP:
                    current_config.APOLLO_NAMESPACE = namespace
                    current_config.access_config_from_function_list(
                        priority=current_config.CONFIGALCHEMY_FUNCTION_VALUE_PRIORITY
                    )
                start_time = time_counter()
        except ConfigException:
            time.sleep(5)
        except Exception:
            logging.exception("long poll error")
