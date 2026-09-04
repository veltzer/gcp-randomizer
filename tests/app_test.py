""" Test the randomizer flask app end to end with webtest. """

import webtest

import main


def test_get():
    """ GET / renders the modes page with all seven modes. """
    application = webtest.TestApp(main.app)

    response = application.get('/')
    assert response.status_int == 200
    for mode in main.MODES:
        assert mode.encode() in response.body


def test_version():
    """ GET /app/version reports the deploy stamp and the serving revision. """
    application = webtest.TestApp(main.app)

    response = application.get('/app/version')
    assert response.status_int == 200
    for key in ("deploy_date", "git_describe", "revision"):
        assert key in response.json
