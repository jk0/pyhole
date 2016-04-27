..
   Copyright 2011-2016 Josh Kearney

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.

Submitting Code
===============

Follow the procedure below when submitting code.

Standard GitHub Workflow
^^^^^^^^^^^^^^^^^^^^^^^^

Start off my forking [#]_ `pyhole <https://github.com/jk0/pyhole>`_ to your account on GitHub.
From here you can make your changes::

    git clone https://github.com/jk0/pyhole.git && cd pyhole

    ...make changes...

    python setup.py flake8
    python setup.py test

    git commit -a -m "Detailed commit message."
    git push origin HEAD

When done, open a Pull Request [#]_ on GitHub.

.. [#] https://help.github.com/articles/fork-a-repo/
.. [#] https://help.github.com/articles/using-pull-requests/
