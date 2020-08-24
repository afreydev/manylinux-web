import requests
import json
import docker
import random
from flask import flash

MANYLINUX_NETWORK = "manylinux-web_manylinux_network"
manylinux_versions = {
    "2010": "many_local",
    "2014": "many_local_2014"
}



def get_versions(form):
    # This get the python version selected from the GUI
    versions = []
    if form.python36.data:
        versions.append("python36")
    if form.python37.data:
        versions.append("python37")
    return versions


def build_wheels(settings, server):
    # Send a rest request to the manylinux container
    # with the settings for the building
    r = requests.post(
        "http://{}:5000/run".format(server),
        json=settings
    )
    return r


def messages(response, flash_messages=True):

    messages = []
    if flash_messages:
        # If is a sync building, it pushes messages using flask
        for m in response.json():
            flash(m["message"], m["type"])
    else:
        # If is an async building append messages in a list
        for m in response.json():
            messages.append({
                "message": m["message"]
            })
    return messages


def create_container_many_linux(settings):
    client = docker.from_env()
    container_name = "manylinux_{}".format(str(random.randint(0, 10000)))
    # Create a new manylinux container with a random name
    # TODO: Improve docker network discovering
    container = client.containers.run(
        manylinux_versions[settings["manylinux_version"]],
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
