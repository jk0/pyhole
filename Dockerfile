FROM ubuntu:trusty

ENV cwd /opt/pyhole

WORKDIR ${cwd}

RUN apt-get update && apt-get install --no-install-recommends -y \
    build-essential \
    ca-certificates \
    libffi-dev \
    libssl-dev \
    python-dev \
    python-setuptools \
 && rm -rf /var/lib/apt/lists/*

COPY . ${cwd}
RUN python setup.py install

EXPOSE 5000

CMD pyhole
