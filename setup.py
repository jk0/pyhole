#   Copyright 2011-2015 Josh Kearney
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

import setuptools

from pyhole.core import version


setuptools.setup(
    name="irc-pyhole",
    version=version.version(),
    author="Josh Kearney",
    author_email="josh@jk0.org",
    description="A modular IRC & Slack bot.",
    url="https://github.com/jk0/pyhole",
    classifiers=[
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python"
    ],
    install_requires=[
        "BeautifulSoup==3.2.0",
        "Eventlet",
        "irc",
        "launchpadlib",
        "pywunderground",
        "requests",
        "slackclient",
        "yahoo-finance"
    ],
    setup_requires=[
        "flake8==2.4.1",
        "sphinx"
    ],
    test_suite="pyhole.tests",
    packages=setuptools.find_packages(),
    entry_points={
        "console_scripts": [
            "pyhole = pyhole.main:Main"
        ]
    }
)
