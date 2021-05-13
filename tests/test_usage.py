# the functionality of this test file has not been tested.
import chromedriver_binary
from dash.testing.application_runners import import_app

## NOTE: Here are some notes for testing
# Naming convention: test_{tcid}_{test title}
# Running just one tcid: python -m pytest -k {tcid}
# General guide: https://dash.plotly.com/testing

# Basic test for the component rendering.
# The dash_duo pytest fixture is installed with dash (v1.0+)
def test_render01_render_component(dash_duo):
    # Start a dash app contained as the variable `app` in `usage.py`
    app = import_app("usage")
    dash_duo.start_server(app)

    # Get the generated component input with selenium
    # The html input will be a children of the #input dash component
    dash_uploader = dash_duo.find_element("#dash-uploader")

    assert "dash-uploader-default" == dash_uploader.get_attribute("class")
