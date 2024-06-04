from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def expect_alert(driver, text, timeout=4):
    """
    Expect an alert in the browser.

    Parameters
    ---------
    driver: webdriver
        The driver that is used in the session
    text: str
        The text or part of the text expected in
        the alert
    timeout: numeric
        The time to wait until timeout error,
        in seconds.

    """
    # Expect to see an error alert text for the user
    # in the following seconds
    WebDriverWait(driver, timeout).until(EC.alert_is_present())
    alert = driver.switch_to.alert
    assert text in alert.text
    # Close alert to prevent UnexpectedAlertPresentException
    alert.accept()


def create_file(filename, filesize_mb=1):
    """
    Create file for testing purposes.

    Parameters
    ----------
    filename: str
        The filename
    filesize_mb: numeric
        The file size in MB.
    """
    with open(filename, "wb") as f:
        f.seek(int(1024 * 1024 * filesize_mb))
        f.write(b"0")


def load_text_file(file_path):
    """
    Load text file from the path

    Parameters
    ----------
    file_path: str
        The path of the file.
    """
    with open(file_path, "r") as f:
        return f.read()
