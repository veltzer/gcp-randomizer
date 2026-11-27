"""
This is the main entry point to the application
"""


import json
import os
import random
import urllib.parse
from typing import TYPE_CHECKING

from flask import Flask, Response, jsonify, redirect, render_template, request

if TYPE_CHECKING:
    from werkzeug.wrappers import Response as WerkzeugResponse

# build_info.json is written next to src/, at the repo (and image) root.
BUILD_INFO = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "build_info.json")

app = Flask(__name__)
# The hostname the site is meant to be reached on (gcp_domain in .gcp.conf);
# empty in development.
app.config["CANONICAL_HOST"] = os.environ.get("CANONICAL_HOST", "")


def load_build_info():
    """ Load the deploy stamp written by gcloud_deploy.sh; absent in dev. """
    try:
        with open(BUILD_INFO, encoding="UTF8") as fp:
            info = json.load(fp)
    except FileNotFoundError:
        info = {"deploy_date": "unknown", "git_describe": "dev"}
    app.config["build_info"] = info


load_build_info()


def build_details():
    """ the deploy stamp plus the serving revision, for /app/version and page footers """
    info = dict(app.config["build_info"])
    # Cloud Run injects the serving revision name at runtime.
    info["revision"] = os.environ.get("K_REVISION", "local")
    return info


def canonical_url() -> str:
    """ this page's address on the canonical host; in development, where there is none, as it was asked for """
    host = app.config["CANONICAL_HOST"]
    if not host:
        return request.base_url
    return urllib.parse.urlunsplit(("https", host, request.path, "", ""))


@app.before_request
def redirect_to_canonical_host() -> WerkzeugResponse | None:
    """
    Cloud Run also answers on its run.app hostnames. Send those to the custom
    domain, so the site has one address. /app/version is exempt, so a
    revision can still be asked directly what it is.
    """
    host = app.config["CANONICAL_HOST"]
    if not host or request.host == host or request.path == "/app/version":
        return None
    url = urllib.parse.urlsplit(request.url)._replace(scheme="https", netloc=host).geturl()
    return redirect(url, code=308)


@app.context_processor
def inject_build_details():
    """ make the build details (`build`) and the page's canonical address available to every template """
    return {"build": build_details(), "canonical_url": canonical_url()}

MODES = [
    "Ionian",
    "Dorian",
    "Phrygian",
    "Lydian",
    "Mixolydian",
    "Aeolian",
    "Locrian"
]

@app.route("/app/version", methods=["GET"])
def version():
    """ the deploy stamp and the serving revision """
    return jsonify(build_details())


@app.route("/favicon.ico", methods=["GET"])
def favicon() -> Response:
    """ the site icon, for clients that ask for /favicon.ico without reading a page's <link rel="icon"> """
    return app.send_static_file("favicon.svg")


@app.route("/")
def root():
    """ The root URL """
    return modes()

@app.route("/modes")
def modes():
    """ show randomized modes """
    randomized_modes = MODES.copy()
    random.shuffle(randomized_modes)
    return render_template("index.html", randomized_modes=randomized_modes)

@app.route("/general", methods=["GET", "POST"])
def general():
    """ this is the root url """
    randomized_list: list[str] = []
    if request.method == "POST":
        items = request.form["items"].split("\n")
        items = [item.strip() for item in items if item.strip()]
        random.shuffle(items)
        randomized_list = items
    return render_template("general.html", randomized_list=randomized_list)

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080, debug=True)
