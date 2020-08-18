import requests
import json
from flask import flash
import docker
import random

MANYLINUX_NETWORK = "manylinux-web_manylinux_network"
MANYLINUNX_IMAGE = "many_local"


def get_versions(form):
    versions = []
    if form.python36.data:
        versions.append("python36")
    if form.python37.data:
        versions.append("python37")
    return versions


def build_wheels(settings, server):
    r = requests.post(
        "http://{}:5000/run".format(server),
        json=settings
    )
    return r

def messages(response, flash_messages=True):
    messages = []
    if flash_messages:
        for m in response.json():
            flash(m["message"], m["type"])
    else:
        for m in response.json():
            messages.append({
                "message": m["message"]
            })
    return messages



def create_container_many_linux():
    client = docker.from_env()
    container_name = "manylinux_{}".format(str(random.randint(0, 1000)))
    container = client.containers.run(
        MANYLINUNX_IMAGE,
        environment=["FLASK_ENV=development"],
        network=MANYLINUX_NETWORK,
        detach=True,
        remove=True,
        name=container_name
    )
    return container_name


def kill_container(container_name):
    client = docker.from_env()
    container = client.containers.get(container_name)
    container.kill()
