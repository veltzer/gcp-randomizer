"""
This is the main entry point to the application
"""


import json
import os
import random
import re
import urllib.parse
from datetime import UTC, datetime
from typing import TYPE_CHECKING

from flask import Flask, Response, jsonify, redirect, render_template, request
from markupsafe import Markup

if TYPE_CHECKING:
    from werkzeug.wrappers import Response as WerkzeugResponse

# build_info.json is written next to src/, at the repo (and image) root.
BUILD_INFO = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "build_info.json")

# where the code lives, for the footer's "built from" line
REPO = "veltzer/gcp-randomizer"

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


def built_line(info: dict[str, str]) -> Markup:
    """
    The footer's last line, as the other sites of the fleet word it: which
    commit of which repository was built, when, and which revision serves it.
    Each part is said only when the deploy stamp really carries it.
    """
    line = Markup("Built")
    commit = re.search(r"(?:-g)?([0-9a-f]{7,40})(?:-dirty)?$", info.get("git_describe") or "")
    if commit:
        line += Markup(' from <a href="https://github.com/{repo}">{repo}</a> commit <a href="https://github.com/{repo}/commit/{commit}"><code>{commit}</code></a>').format(
            repo=REPO, commit=commit.group(1),
        )
    stamp = deploy_stamp(info)
    if stamp:
        line += Markup(' on <time datetime="{date}">{text} UTC</time>').format(date=info["deploy_date"], text=stamp.replace("T", " "))
    if info["revision"] == "local":
        return line + " (local)"
    return line + Markup(", serving as {revision}").format(revision=info["revision"])


def deploy_stamp(info: dict[str, str]) -> str:
    """ the deploy time to the minute (2026-11-27T19:37), or nothing when the stamp holds no real date """
    stamp = re.match(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}", info.get("deploy_date") or "")
    return stamp.group() if stamp else ""


def provenance() -> dict[str, str]:
    """
    What the page footer says about where the page came from. The copyright
    year is read off the deploy stamp, so the same deploy always says the same.
    """
    info = build_details()
    stamp = deploy_stamp(info)
    return {
        "year": stamp[:4] if stamp else str(datetime.now(UTC).year),
        "built": built_line(info),
    }


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
    """ make the footer's provenance (`site`) and the page's canonical address available to every template """
    return {"site": provenance(), "canonical_url": canonical_url()}

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
