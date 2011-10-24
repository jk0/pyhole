..
   Copyright 2011 Josh Kearney

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.

Installation
============

From Source
^^^^^^^^^^^

::

    git clone git://github.com/jk0/pyhole.git
    cd pyhole
    sudo pip install -r tools/pip-requires
    ./tools/run_pyhole.sh
    vi ~/.pyhole/pyhole.conf
    ./tools/run_pyhole.sh

Python Package
^^^^^^^^^^^^^^

::

    pip install irc-pyhole
    pyhole
    vi ~/.pyhole/pyhole.conf
    pyhole
