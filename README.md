# pyhole - A modular IRC & Slack bot.

[![Build Status](https://travis-ci.org/jk0/pyhole.svg?branch=master)](https://travis-ci.org/jk0/pyhole) [![Doc Status](https://readthedocs.org/projects/irc-pyhole/badge/?version=latest)](https://readthedocs.org/projects/irc-pyhole/)

## Installation

````
git clone https://github.com/jk0/pyhole.git && cd pyhole
````

### Source

```
virtualenv venv
. venv/bin/activate

python setup.py flake8
python setup.py test
python setup.py develop

pyhole
````

### Docker

```
bash tools/docker_deploy.sh
```
