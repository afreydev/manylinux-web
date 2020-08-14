FROM quay.io/pypa/manylinux2010_x86_64

ENV PLAT manylinux201i0_x86_64
ENV FLASK_APP=/opt/webserver/server.py

# Creating a venv for python packages
RUN /opt/python/cp37-cp37m/bin/python -m venv /opt/venv
RUN . /opt/venv/bin/activate && pip install Flask twine gitpython

COPY server.py /opt/webserver/

WORKDIR /opt/webserver

CMD . /opt/venv/bin/activate && flask run --host=0.0.0.0