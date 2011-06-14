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

Coding Guidelines
=================

When contributing to the pyhole project, please be sure to read over the
following information.

Python Style
-------------

General
^^^^^^^

* Two newlines between toplevel imports, classes, functions, etc
* One newline between anything not mentioned above
* Make an honest effort at not catching all exceptions
* Do not name anything the same as builtin or reserved words
* Use double quotes (") whenever possible
* Everything must be PEP8-compliant: http://www.python.org/dev/peps/pep-0008/

Imports
^^^^^^^

* Import only modules
* Import one module per line
* Imports are grouped by *import* and *from*
* Imports should be in alphabetical order in their groups

::

    import re
    import urllib

    from BeautifulSoup import BeautifulSoup

    from pyhole import plugin
    from pyhole import utils

Docstrings
^^^^^^^^^^

::

    """This is a single-line docstring"""

    """This is a multi-line docstring

    Second paragraph goes like this. Ending quotes are on their own line.
    """

Indentation
^^^^^^^^^^^

Should a line flow over 79 characters, you will indent as such: ::

    log = logging.handlers.TimedRotatingFileHandler("%s/%s.log" % (log_dir,
            name.lower()), "midnight")

Make note of the double indent (8 characters in length).

Testing
-------

Every new piece of code must be covered by a unit test. One must also ensure
that all tests pass before submitting code. Testing examples can be found in
the *tests* directory.
