"""
This is the main entry point to the application
"""


import json
import os
import random

from flask import Flask, jsonify, render_template, request

app = Flask(__name__)


def load_build_info():
    """ Load the deploy stamp written by gcloud_run_deploy.sh; absent in dev. """
    try:
        with open("build_info.json", encoding="UTF8") as fp:
            info = json.load(fp)
    except FileNotFoundError:
        info = {"deploy_date": "unknown", "git_describe": "dev"}
    app.config["build_info"] = info


load_build_info()

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
    info = dict(app.config["build_info"])
    # Cloud Run injects the serving revision name at runtime.
    info["revision"] = os.environ.get("K_REVISION", "local")
    return jsonify(info)


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
    randomized_list = []
    if request.method == "POST":
        items = request.form["items"].split("\n")
        items = [item.strip() for item in items if item.strip()]
        random.shuffle(items)
        randomized_list = items
    return render_template("general.html", randomized_list=randomized_list)

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080, debug=True)
