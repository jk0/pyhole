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

Submitting Code
===============

Follow the procedure below when submitting code.

Standard GitHub Workflow
^^^^^^^^^^^^^^^^^^^^^^^^

Start off my forking [#]_ `pyhole <https://github.com/jk0/pyhole>`_ to your account on GitHub.
From here you can make your changes::

    git clone git://github.com/<GitHub ID>/pyhole.git
    cd pyhole

    ...make changes...

    ./tools/run_tests.sh
    git commit -a -m "Detailed commit message."
    git push

When done, open a Pull Request [#]_ on GitHub.

.. [#] http://help.github.com/fork-a-repo/
.. [#] http://help.github.com/send-pull-requests/
