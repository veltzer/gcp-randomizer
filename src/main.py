"""
This is the main entry point to the application
"""


import random
from flask import Flask, render_template, request

app = Flask(__name__)

MODES = [
    "Ionian",
    "Dorian",
    "Phrygian",
    "Lydian",
    "Mixolydian",
    "Aeolian",
    "Locrian"
]

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

@app.route("/general")
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
