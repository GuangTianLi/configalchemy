"""Unit test package for configalchemy."""
from configalchemy.lazy import lazy, proxy


def get_name():
    print("evaluating")
    return "World"


lazy_name = lazy(get_name)
print(f"Hello {lazy_name}")
print(f"Hello {lazy_name}")

proxy_name = proxy(get_name)
print(f"Hello {proxy_name}")
print(f"Hello {proxy_name}")
