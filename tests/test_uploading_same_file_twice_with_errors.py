import shutil
import sys
import threading
import time
from pathlib import Path

import chromedriver_binary
import pytest
from dash.testing.application_runners import import_app
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from .utils import create_file

# On *nix or not?
ON_NIX = sys.platform in ["linux", "darwin"]


@pytest.fixture
def testfile10kb_csv():
    file = Path(__file__).resolve().parent / "testfile_for_reupload.csv"
    create_file(file, filesize_mb=10 / 1024)
    yield file
    file.unlink()


@pytest.fixture
def testfile10kb_2_csv():
    file = Path(__file__).resolve().parent / "testfile2_for_reupload.csv"
    create_file(file, filesize_mb=10 / 1024)
    yield file
    file.unlink()


def reserve_file_for_while_on_windows(filepath, wait_time):
    f = open(filepath, "r")  # reserves the file on Windows
    time.sleep(wait_time)
    f.close()


HOLD_TIME_FOR_FILE = 1.5  # seconds


def test_uploadtwice01_upload_a_file_twice_and_reserve_it(
    dash_duo, testfile10kb_csv, testfile10kb_2_csv
):
    # This simulates the case when sometimes for some reason
    # the file might get reserved. (e.g. because of antivirus check, Windows
    # indexing or similar.) (Happens escpecially (only?) on Windows)
    #
    # (1) Upload a file
    # (2) Reserve that file for a while
    # (3) Try to upload the file
    # (4) Release the file
    # (5) The second upload of the same file should be okay

    app = import_app("tests.apps.testapp")
    dash_duo.start_server(app)

    def upload_file(file_to_upload):
        # User sees the component
        upload = dash_duo.find_element("#dash-uploader")

        # Upload the file.
        # Clicking the upload component would open a file dialog and
        # this would require the tests to use OS specific GUI tools
        # to select the file. This could be added in the future but it's
        # probably very this would be broken
        upload_input = upload.find_element(
            By.XPATH, "//input[@name='dash-uploader-upload']"
        )
        upload_input.send_keys(str(file_to_upload))

    upload_file(testfile10kb_csv)

    # Wait for "Completed: testfile_for_reupload.csv" text, with 10 second timeout
    WebDriverWait(dash_duo._driver, 10).until(
        EC.text_to_be_present_in_element(
            (By.XPATH, "//div[@id='dash-uploader']/*/label"), testfile10kb_csv.name
        )
    )

    # Get the div with the output values
    callback_output = dash_duo.find_element("#callback-output")
    # Get the name of the uploaded file
    uploaded_file = callback_output.find_element(By.XPATH, "//ul").text
    uploaded_file = Path(uploaded_file)

    assert uploaded_file.name == testfile10kb_csv.name
    assert uploaded_file.exists()
    assert uploaded_file.stat().st_size == testfile10kb_csv.stat().st_size

    # Upload another file to change the labels.
    upload_file(testfile10kb_2_csv)
    # Wait for "Completed: testfile2_for_reupload.csv" text, with 10 second timeout
    WebDriverWait(dash_duo._driver, 10).until(
        EC.text_to_be_present_in_element(
            (By.XPATH, "//div[@id='dash-uploader']/*/label"), testfile10kb_2_csv.name
        )
    )
    # Wait that the callback for the 'testfile2_for_reupload.csv' has been fired.
    WebDriverWait(dash_duo._driver, 10).until(
        EC.text_to_be_present_in_element(
            (By.XPATH, '//*[@id="callback-output"]/ul/li'), testfile10kb_2_csv.name
        )
    )

    # Reserve file & make it impossible to upload testfile10kb_csv
    # Hold the file for 1.5 seconds
    file_reserve_thread = threading.Thread(
        target=reserve_file_for_while_on_windows,
        args=(uploaded_file, HOLD_TIME_FOR_FILE),
    )
    file_reserve_thread.start()

    # Reupload file again with same filename
    upload_file(testfile10kb_csv)

    # Wait until file is uploaded (2nd time)
    # Wait for "Completed: testfile_for_reupload.csv" text, with 6 second timeout
    WebDriverWait(dash_duo._driver, 6).until(
        EC.text_to_be_present_in_element(
            (By.XPATH, "//div[@id='dash-uploader']/*/label"), testfile10kb_csv.name
        )
    )

    # Get the div with the output values (2nd time)
    callback_output = dash_duo.find_element("#callback-output")

    # Get the name of the uploaded file (2nd time)
    uploaded_file = callback_output.find_element(By.XPATH, "//ul").text
    uploaded_file = Path(uploaded_file)

    assert uploaded_file.name == testfile10kb_csv.name
    assert uploaded_file.exists()
    assert uploaded_file.stat().st_size == testfile10kb_csv.stat().st_size

    # cleanup
    file_reserve_thread.join()
    shutil.rmtree(uploaded_file.parent)


# Run with pytest -k uploadtwice02
@pytest.mark.skipif(
    ON_NIX,
    reason=(
        "Opening a file is not blocking on Linux and MacOS, and there was problem only"
        " on Windows. Therefore, the test needs also to be ran on Windows."
    ),
)
def test_uploadtwice02_upload_a_file_twice_with_error(
    dash_duo, testfile10kb_csv, testfile10kb_2_csv
):
    # Same as test_uploadtwice01_upload_a_file_twice_and_reserve_it
    # but force an error. This is only tested on Windows as the original
    # problem may only occur on Windows. (or, at least seems not the be easily
    # reproducible on Linux)

    # This app does not have retries on the "remove_file"
    # function, and therefore the error alert will appear
    # to the user instantly. (to make tests faster)
    app = import_app("tests.apps.testapp_noretry_remove_file")
    dash_duo.start_server(app)

    def upload_file(file_to_upload):
        # User sees the component
        upload = dash_duo.find_element("#dash-uploader")

        # Upload the file.
        # Clicking the upload component would open a file dialog and
        # this would require the tests to use OS specific GUI tools
        # to select the file. This could be added in the future but it's
        # probably very this would be broken
        upload_input = upload.find_element(
            By.XPATH, "//input[@name='dash-uploader-upload']"
        )
        upload_input.send_keys(str(file_to_upload))

    upload_file(testfile10kb_csv)

    # Wait for "Completed: testfile_for_reupload.csv" text, with 10 second timeout
    WebDriverWait(dash_duo._driver, 10).until(
        EC.text_to_be_present_in_element(
            (By.XPATH, "//div[@id='dash-uploader']/*/label"), testfile10kb_csv.name
        )
    )

    # Get the div with the output values
    callback_output = dash_duo.find_element("#callback-output")
    # Get the name of the uploaded file
    uploaded_file = callback_output.find_element(By.XPATH, "//ul").text
    uploaded_file = Path(uploaded_file)

    assert uploaded_file.name == testfile10kb_csv.name
    assert uploaded_file.exists()
    assert uploaded_file.stat().st_size == testfile10kb_csv.stat().st_size

    # Upload another file to change the labels.
    upload_file(testfile10kb_2_csv)
    # Wait for "Completed: testfile2_for_reupload.csv" text, with 10 second timeout
    WebDriverWait(dash_duo._driver, 10).until(
        EC.text_to_be_present_in_element(
            (By.XPATH, "//div[@id='dash-uploader']/*/label"), testfile10kb_2_csv.name
        )
    )
    # Wait that the callback for the 'testfile2_for_reupload.csv' has been fired.
    WebDriverWait(dash_duo._driver, 10).until(
        EC.text_to_be_present_in_element(
            (By.XPATH, '//*[@id="callback-output"]/ul/li'), testfile10kb_2_csv.name
        )
    )

    # Reserve file & make it impossible to upload testfile10kb_csv
    # Hold the file for 4 seconds
    file_reserve_thread = threading.Thread(
        target=reserve_file_for_while_on_windows,
        args=(uploaded_file, HOLD_TIME_FOR_FILE),
    )
    file_reserve_thread.start()

    # Reupload file again with same filename
    upload_file(testfile10kb_csv)

    # Expect to see an error alert text for the user
    # in the following seconds
    WebDriverWait(dash_duo._driver, 4).until(EC.alert_is_present())

    alert = dash_duo._driver.switch_to.alert
    assert (
        "Unexpected error while uploading testfile_for_reupload.csv!\nPlease reupload the file."
        in alert.text
    )

    # cleanup
    file_reserve_thread.join()
    shutil.rmtree(uploaded_file.parent)
