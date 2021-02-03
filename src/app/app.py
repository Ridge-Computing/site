import os
from pathlib import Path
from urllib.parse import urljoin

from flask import Flask, render_template
import redis as r

app = Flask(
    "RidgeComputing",
    template_folder=Path.cwd() / "app" / "templates",
)
app.secret_key = os.urandom(24)
app.config["STATIC"] = "https://cdn.jsdelivr.net/gh/Ridge-Computing/static/"
app.config["COLOR"] = "#009e54"


def cdn_for(filename):
    return urljoin(app.config["STATIC"], filename)


def desc_for(uuid):
    return f'uuid/{int(uuid)}.html'


app.jinja_env.globals.update(cdn_for=cdn_for, desc_for=desc_for, brand_color=app.config["COLOR"])

db = r.Redis(host="localhost", port=6379, db=0)

from .models import UserData, CourseData, BranchData, OrgData

app.jinja_env.globals.update(courses=CourseData, users=UserData, branches=BranchData, orgs=OrgData)


# main site
@app.route('/', methods=['GET'])
def index():
    return render_template("index.html")


@app.route('/courses/', methods=['GET'])
def courses():
    return render_template("courses.html")


@app.route('/about/', methods=['GET'])
def about():
    return render_template("about.html")


@app.route('/contact/', methods=['GET'])
def contact():
    return render_template("contact.html")


@app.route('/chapter/<string:branch>', methods=['GET'])
def chapter(branch):
    try:
        branch = BranchData.branch(branch)
    except AttributeError:
        return render_template('404.html'), 404
    return render_template("branch.html", chapter=branch)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html')
