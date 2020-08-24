import os
import sys
import shutil
import subprocess
import time
import json
from flask import (
    Flask,
    request,
    jsonify,
    render_template,
    redirect,
    url_for,
    flash
)
from flask_bootstrap import Bootstrap
from forms import BuildForm
from decouple import config
from celery_app import make_celery
from celery.result import AsyncResult
import manylinux
import docker
import db


app = Flask(__name__)

app.config.update(dict(
    SECRET_KEY=config("SECRET_KEY"),
    WTF_CSRF_SECRET_KEY=config("WTF_CSRF_SECRET_KEY"),
    CELERY_BROKER_URL=config("CELERY_BROKER_URL"),
    CELERY_RESULT_BACKEND=config("CELERY_RESULT_BACKEND"),
    MYSQL_HOST=config("MYSQL_HOST"),
    MYSQL_ROOT_PASSWORD=config("MYSQL_ROOT_PASSWORD"),
    MYSQL_DATABASE=config("MYSQL_DATABASE"),
    MYSQL_USER=config("MYSQL_USER"),
    MYSQL_PASSWORD=config("MYSQL_PASSWORD"),
    MANAGEMENT_TOKEN=config("MANAGEMENT_TOKEN"),
))

bootstrap = Bootstrap(app)
celery = make_celery(app)


@app.route('/', methods=['GET', 'POST'])
def index():
    form = BuildForm()
    if form.validate_on_submit():
        settings = {
            "git": form.git.data,
            "versions": manylinux.get_versions(form),
            "manylinux_version": form.manylinux_version.data
        }

        if form.async_build.data:
            # When the user select an async build it create a celery task
            task = build_task.delay(settings, False)
            db.create_task(app, settings, task.id)
            flash("Wait a moment for task: {}".format(task.id), "MES")
            return redirect(url_for('tasks'))
        else:
            build(settings, True)
            return redirect(url_for('index'))

    return render_template('index.html', form=form)


@app.route('/tasks', methods=['GET'])
def tasks():
    limit = request.args.get('limit', default="10")
    tasks = db.get_tasks(app, int(limit))
    return render_template('tasks.html', tasks=tasks)


@app.route('/management', methods=['GET'])
def management():
    # This route is only for creating the table to track the async tasks
    task = request.args.get('task', default="")
    token = request.args.get('token', default="")
    if task == "create-table" and token == app.config["MANAGEMENT_TOKEN"]:
        return str(db.create_table(app))
    elif task == "truncate-table" and token == app.config["MANAGEMENT_TOKEN"]:
        return str(db.truncate_table(app))


def build(settings, flash):
    container_name = manylinux.create_container_many_linux(settings)
    # TODO: Improve container creation sync
    time.sleep(10)
    response = manylinux.build_wheels(settings, container_name)
    m = manylinux.messages(response, flash)
    manylinux.kill_container(container_name)
    return m


def get_status(task_id):
    task = AsyncResult(task_id)
    return task.state


def get_result(task_id):
    task = AsyncResult(task_id)
    if task.result is None:
        return []
    return task.result


def get_settings(settings_text):
    return json.loads(settings_text.replace("'","\""))


def to_pretty_json(value):
    return json.dumps(value, sort_keys=True,
                      indent=4, separators=(',', ': '))


@celery.task()
def build_task(settings, flash):
    # This wraps the build function
    return build(settings, flash)


app.jinja_env.filters['tojson_pretty'] = to_pretty_json
app.add_template_global(get_settings, name='get_settings')
app.add_template_global(get_result, name='get_result')
app.add_template_global(get_status, name='get_status')
