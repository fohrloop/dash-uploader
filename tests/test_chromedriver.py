"""
A module to test that the correct ChromeDriver 
version is installed for the tests.

The tests in this module are ran before other tests.
(ordering is edited in the conftest.py:pytest_collection_modifyitems)
"""

import re
import warnings

from selenium.common.exceptions import SessionNotCreatedException
from selenium import webdriver
import chromedriver_binary  # Adds chromedriver binary to path


OLD_CHROMEDRIVER_ERROR_MSG = """
        !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        !!!                                  !!!
        !!! Wrong ChromeDriver version found !!!
        !!!                                  !!!
        !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

        The tests cannot be run! Please, install the correct
        version of ChromeDriver with 

        python -m pip install --upgrade --force-reinstall chromedriver-binary{VERSION}
        
        """


def test_chromedriver_version_okay():
    try:
        webdriver.Chrome()
    except SessionNotCreatedException as e:
        match = re.search("browser version is (\d+)\.", str(e))
        if match:
            version_str = "==" + match.groups()[0] + ".*"
        else:
            version_str = ""
        msg = OLD_CHROMEDRIVER_ERROR_MSG.format(VERSION=version_str)

        print(msg)
        warnings.warn(msg)
        raise e
