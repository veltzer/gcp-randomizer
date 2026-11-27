""" Test the randomizer flask app end to end with webtest. """

from typing import TYPE_CHECKING

import webtest

import main

if TYPE_CHECKING:
    import pytest


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


def test_favicon():
    """ the icon is served under /static, named by every page, and answers /favicon.ico. """
    application = webtest.TestApp(main.app)

    icon = application.get('/static/favicon.svg')
    assert icon.status_int == 200
    assert icon.content_type == "image/svg+xml"
    for path in ('/', '/general'):
        assert b'<link rel="icon" type="image/svg+xml" href="/static/favicon.svg">' in application.get(path).body
    response = application.get('/favicon.ico')
    assert response.content_type == "image/svg+xml"
    assert response.body == icon.body


def test_stylesheet():
    """ the shared stylesheet is served and every page links it. """
    application = webtest.TestApp(main.app)

    style = application.get('/static/style.css')
    assert style.status_int == 200
    assert style.content_type == "text/css"
    for path in ('/', '/general'):
        assert b'<link rel="stylesheet" href="/static/style.css">' in application.get(path).body


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


def test_canonical_host(monkeypatch: pytest.MonkeyPatch):
    """ with a canonical host set, other hostnames redirect to it and pages name it. """
    monkeypatch.setitem(main.app.config, "CANONICAL_HOST", "randomizer.veltzer.org")
    application = webtest.TestApp(main.app)

    response = application.get('/general?x=1', extra_environ={"HTTP_HOST": "randomizer-123.us-central1.run.app"})
    assert response.status_int == 308
    assert response.location == "https://randomizer.veltzer.org/general?x=1"
    # a revision can still be asked what it is on any hostname
    assert application.get('/app/version', extra_environ={"HTTP_HOST": "randomizer-123.us-central1.run.app"}).status_int == 200

    response = application.get('/general', extra_environ={"HTTP_HOST": "randomizer.veltzer.org"})
    assert response.status_int == 200
    assert b'<link rel="canonical" href="https://randomizer.veltzer.org/general">' in response.body


def test_no_canonical_host():
    """ without a canonical host (development) nothing redirects and a page names the address it was asked on. """
    application = webtest.TestApp(main.app)

    response = application.get('/', extra_environ={"HTTP_HOST": "anything.example"})
    assert response.status_int == 200
    assert b'<link rel="canonical" href="http://anything.example/">' in response.body
