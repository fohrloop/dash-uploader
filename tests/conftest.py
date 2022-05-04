from collections import defaultdict
from selenium import webdriver


def pytest_setup_options():
    options = webdriver.ChromeOptions()
    # Removes a bunch of errors on Windows, like
    # USB: usb_device_win.cc:93 Failed to read descriptors from ...
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    return options


def pytest_collection_modifyitems(items):
    """
    Modifies test items to ensure test modules run in a given order.
    """
    N_items = len(items)
    # The test_chromedriver.py has tests that test
    # it the tests can be run; run it first.
    FIRST_MODULES = ["tests.test_chromedriver", "tests.test_usage"]

    items_mapping = defaultdict(list)
    for item in items:
        items_mapping[item.module.__name__].append(item)

    sorted_items = []
    for modulename in FIRST_MODULES:
        sorted_items += items_mapping.pop(modulename, [])
    # all other modules
    for modulename, moduleitems in items_mapping.items():
        sorted_items += moduleitems

    items[:] = sorted_items
    assert (
        len(items) == N_items
    ), "Tests dropped out in reordering! This should never happen."
    return items
