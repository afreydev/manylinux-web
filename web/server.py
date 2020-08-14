import os, sys, shutil, subprocess
from flask import (
    Flask,
    request,
    jsonify,
    render_template,
    redirect,
    url_for
)
from flask_bootstrap import Bootstrap
from forms import BuildForm
import manylinux
import docker
import time

app = Flask(__name__)

app.config.update(dict(
    SECRET_KEY="Kasri823udjfla0",
    WTF_CSRF_SECRET_KEY="Kaaix9ss8akjxso9zkaIsk8"
))

bootstrap = Bootstrap(app)


@app.route('/', methods=['GET', 'POST'])
def index():
    form = BuildForm()
    if form.validate_on_submit():
        container_name = manylinux.create_container_many_linux()
        time.sleep(10)
        settings = {
            "git": form.git.data,
            "versions": manylinux.get_versions(form)
        }
        manylinux.build_wheels(settings, container_name)
        manylinux.kill_container(container_name)
        return redirect(url_for('index'))

    return render_template('index.html', form=form)
