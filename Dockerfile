FROM ubuntu:xenial

ENV cwd /opt/pyhole

WORKDIR ${cwd}

RUN apt-get update && apt-get install -y \
    build-essential \
    ca-certificates \
    libffi-dev \
    libssl-dev \
    python-dev \
    python-setuptools \
    python-virtualenv \
 && rm -rf /var/lib/apt/lists/*

COPY . ${cwd}

RUN virtualenv venv && . venv/bin/activate
RUN python setup.py develop

EXPOSE 5000

CMD . venv/bin/activate && pyhole
