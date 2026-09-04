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


def test_general_post():
    """ POST /general shuffles the submitted lines and drops blank ones. """
    application = webtest.TestApp(main.app)

    assert application.get('/general').status_int == 200
    response = application.post('/general', {"items": "scales\n\narpeggios\nchords\n"})
    assert response.status_int == 200
    for item in ("scales", "arpeggios", "chords"):
        assert item.encode() in response.body
    assert b"Randomized List" in response.body


def test_build_details_in_footer():
    """ every page shows the build details in its footer. """
    application = webtest.TestApp(main.app)

    build = main.build_details()
    for path in ('/', '/general'):
        response = application.get(path)
        assert f"build {build['git_describe']}".encode() in response.body
        assert f"deployed {build['deploy_date']}".encode() in response.body
        assert b"revision local" in response.body
