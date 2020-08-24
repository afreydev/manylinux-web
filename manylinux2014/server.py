from flask import Flask, request, jsonify
import subprocess, os, sys, shutil
from git import Repo

app = Flask(__name__)

python_version_av = {
    "python36": "cp36-cp36m",
    "python37": "cp37-cp37m",
}
dirpath = "/opt/src/dist"

@app.route('/')
def many_linux():
    return 'Many Linux, here I am!'

@app.route('/run', methods=['POST'])
def run():
    data = request.get_json()
    commands = []
    messages = []
    Repo.clone_from(data["git"], "/opt/src")
    for python_version in data["versions"]:
        command = "/opt/python/{}/bin/pip wheel . -w ./dist --no-deps".format(python_version_av[python_version])
        return_v = subprocess.call(command.split(), stdout=subprocess.PIPE, cwd="/opt/src")
        if return_v != 0:
            messages.append({"type":"WAR", "message": "Fail building for: {}".format(python_version)})
        else:
            messages.append({"type":"MES", "message": "Success building for: {}".format(python_version)})
    
    command = "twine upload -u monadical -p monadical --repository-url http://pypi:8080 dist/*"
    return_v = subprocess.call(command.split(), stdout=subprocess.PIPE, cwd="/opt/src")
    if return_v != 0:
        messages.append({"type":"WAR", "message": "Fail sending wheels to pypiserver"})
    else:
        messages.append({"type":"MES", "message": "Success publishing in pypiserver"})
     
    return jsonify(messages)
